from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.cqlengine import columns
from cassandra.policies import RetryPolicy
from lcmap import config
import datetime
import numpy as np
import numpy.ma as ma
import logging


logger = logging.getLogger()

auth_provider = PlainTextAuthProvider(username=config.CASSANDRA_USER, password=config.CASSANDRA_PWD)


def get_cluster():
    return Cluster(
        config.CASSANDRA_HOSTS,
        protocol_version=config.CASSANDRA_PROTOCOL_VERSION,
        compression=True,
        default_retry_policy=RetryPolicy(),
        auth_provider=auth_provider)


def get_session(cluster):
    return cluster.connect(config.CASSANDRA_KEYSPACE)


def prepare_select(session):
    return session.prepare("""
      SELECT x, y, satellite, instrument, layer, acquired, metadata, data FROM epsg_5070 WHERE
        x = ? AND
        y = ? AND
        satellite = ? AND
        instrument = ? AND
        layer = ? AND
        acquired > ? AND
        acquired < ?
      """)


def prepare_insert(session):
    return session.prepare("""
        INSERT INTO epsg_5070 (
          x,
          y,
          satellite,
          instrument,
          layer,
          acquired,
          metadata,
          data
          ) VALUES (?,?,?,?,?,?,?,?)
      """)


def as_array(row, size=config.TILE_SIZE):
    """Convert raw data into an array.

    The array, although it is two-dimensional in concept, is actually
    three dimension because the value is contained in a one element
    array.

    This makes it much easier to concat arrays into three-dimensional
    time series.  This could be wrong (or unecessary) but I'm still
    new to using numpy.
    """
    arr = np.ma.frombuffer(row.data)
    arr.set_fill_value(np.nan)
    arr.mask = np.isnan(arr)
    return np.resize(arr, [size, size, 1])


def day_z(date):
    """Calculate an absolute relative number of days.

    This is useful for time-series analysis, and alleviates the model from
    having to do date acrobatics.

    Utlimately, this needs to be relative to something earlier than 1999 for
    purposes of the CCDC.
    """
    jan99 = datetime.datetime(1999, 1, 1)
    return (date-jan99).days


class QueryManager(object):

    def __init__(self):
        cluster = get_cluster()
        self.session = get_session(cluster)
        self.select = prepare_select(self.session)

    def search(self, x, y, satellite, instrument, layer, t1, t2, masks=None):
        """Find a layer and mask it using others."""
        t1 = datetime.datetime.strptime(t1, "%Y-%m-%d")
        t2 = datetime.datetime.strptime(t2, "%Y-%m-%d")
        layer_results = self.session.execute(
            self.select, parameters=(x, y, satellite, instrument, layer, t1, t2),
            timeout=config.CASSANDRA_QUERY_TIMEOUT)

        logger.debug('layer type = {0}, len = {1}'.format(type(layer_results), len(layer_results)))
        if len(layer_results) == 0:
            return

        layer_cube = np.ma.dstack([as_array(r) for r in layer_results])
        logger.debug('layer cube = {0}'.format(layer_cube.shape))

        if masks is not None:
            for mask in masks:
                mask_results = self.session.execute(
                    self.select, parameters=(x, y, satellite, instrument, mask, t1, t2),
                    timeout=config.CASSANDRA_QUERY_TIMEOUT)
            if len(mask_results) > 0:
                mask_cube = np.ma.dstack([as_array(r) for r in mask_results])
                logger.debug('mask cube = {0}'.format(mask_cube.shape))
                layer_cube.mask = mask_cube
            else:
                logger.info('mask not found: {0}'.format(mask))

        timestamps = [day_z(r.acquired) for r in layer_results]
        return layer_cube, timestamps


# import logging
# logger = logging.getLogger(__name__)
