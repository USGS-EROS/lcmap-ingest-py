from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
import datetime
import numpy as np
import numpy.ma as ma
import config


cluster = Cluster(config.CASSANDRA_HOSTS)
session = cluster.connect(config.CASSANDRA_KEYSPACE)


select = session.prepare("""
SELECT extent_x, extent_y, layer_id, acquired_at, data, type FROM tiles WHERE
  projection = ? AND
  extent_x = ? AND
  extent_y = ? AND
  layer_id = ? AND
  acquired_at > ? AND
  acquired_at < ?
""")

insert  = session.prepare("""
  INSERT INTO tiles (
    projection,
    extent_x,
    extent_y,
    layer_id,
    acquired_at,
    data,
    type
    ) VALUES (?,?,?,?,?,?,?)
""")


def save(projection, extent_x, extent_y, layer, acquired, data):
    return session.execute(insert, (projection, extent_x, extent_y,
                           layer, acquired, data, str(data.dtype)))


def find(projection="EPSG:5070", x=None, y=None, layer=None, t1=None, t2=None):
    """Find a layer, no masking, no data to array conversion."""
    t1 = datetime.datetime.strptime(t1, "%Y-%m-%d")
    t2 = datetime.datetime.strptime(t2, "%Y-%m-%d")
    results = session.execute(
        select, parameters=(projection, x, y, layer, t1, t2))
    return results


def search(projection, x, y, layer, t1, t2, masks=None):
    """Find a layer and mask it using others."""
    t1 = datetime.datetime.strptime(t1, "%Y-%m-%d")
    t2 = datetime.datetime.strptime(t2, "%Y-%m-%d")
    timeout = 60.0
    data_results = session.execute(
        select, parameters=(projection, x, y, layer, t1, t2), timeout=timeout)

    data_cube = np.dstack([as_array(r) for r in data_results])
    data_cube = ma.masked_equal(data_cube, -9999)

    if masks:
        for mask in masks:
            mask_results = session.execute(
                select, parameters=(projection, x, y, mask, t1, t2), timeout=timeout)
            if mask_results:
                mask_cube = np.dstack([as_array(m) for m in mask_results])
                data_cube = ma.masked_array(data_cube, mask_cube)
            else:
                print("Mask not found: %s" % mask)

    timestamps = [day_z(r.acquired_at) for r in data_results]

    return data_cube, timestamps


def as_array(row, size=1000):
    """Convert raw data into an array.

    The array, although it is two-dimensional in concept, is actually
    three dimension because the value is contained in a one element
    array.

    This makes it much easier to concat arrays into three-dimensional
    time series.  This could be wrong (or unecessary) but I'm still
    new to using numpy.
    """
    return np.resize(np.fromstring(row.data, dtype=row.type), [size, size, 1])


def day_z(date):
  """Calculate an absolute relative number of days.

  This is useful for time-series analysis, and alleviates the model from
  having to do date acrobatics.

  Utlimately, this needs to be relative to something earlier than 1999 for
  purposes of the CCDC.
  """


  jan99 = datetime.datetime(1999, 1, 1)
  return (date-jan99).days


import logging
logger = logging.getLogger(__name__)