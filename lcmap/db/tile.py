from lcmap import config
from lcmap.ingest import util
from lcmap.db.connection import session
from cassandra.concurrent import execute_concurrent_with_args
from datetime import datetime
import lcmap.db.util as db_util


import logging
logger = logging.getLogger(__name__)


SAVE_CQL = """INSERT INTO epsg_5070 (x, y, layer, source, acquired, data,
              data_type, data_fill, data_range, data_scale, data_shape)
    VALUES (?,?,?,?,?,?,
            ?,?,?,?,?)"""

SAVE = session.prepare(SAVE_CQL)


def save(x, y, layer, source, acquired, data, data_type, data_fill, data_range, data_scale, data_shape, **kwargs):
    """Save"""
    logger.debug("Saving <%s,%s> (%s:%s) @ %s - %s" %
                 (x, y, layer, source, acquired, data_type))
    parameters = (x, y, layer, source, acquired, data,
                  data_type, data_fill, data_range, data_scale, data_shape)
    return session.execute(SAVE, parameters)


FIND_CQL = """SELECT * FROM epsg_5070 WHERE
    x = ? AND y = ? AND layer in ? AND acquired > ? AND acquired < ?"""

FIND = session.prepare(FIND_CQL)


def find(x, y, layer, t1, t2):
    """Find a tile containing x, y.

    This does not post-process results. It returns a list of rows results
    that can be further processed. This means that the data blob isn't even
    a usable array.
    """
    logger.debug("find <%s,%s> (%s) @ %s-%s." % (layer, x, y, t1, t2))
    t1 = datetime.strptime(t1, "%Y-%m-%d")
    t2 = datetime.strptime(t2, "%Y-%m-%d")
    parameters = (x, y, layer, t1, t2)
    results = session.execute(FIND, parameters)
    return results


def find_area(x1, y1, x2, y2, layers, t1, t2, grid=30 * 100):
    """Find an area containing x1:x2, y1:y2.

    Like find, this function does not post-process results. This is a simple
    low-level function that can be wrapped with mosaic and subsetting code
    to further ease making results more usable.
    """
    # Find the tile coordinates containing upper left...
    ux, uy = util.snap(x1, y1)
    # ...and the lower right points
    lx, ly = util.snap(x2, y2)

    # TODO - offset?  something must be wrong somewhere
    x_offset = -600
    y_offset = -200
    xs = range(ux + x_offset, lx + x_offset, grid)
    ys = range(uy + y_offset, ly + y_offset, -1 * grid)

    # We only support one basic date format...
    dtfmt = "%Y-%m-%d"
    t1, t2 = datetime.strptime(t1, dtfmt), datetime.strptime(t2, dtfmt)

    # support a list of layers which is faster than individual queries for each layer
    if isinstance(layers, str):
        layers = [layers]

    args = [(tx, ty, layers, t1, t2) for ty in ys for tx in xs]
    logger.info('num of statments = {0}'.format(len(args)))
    results = execute_concurrent_with_args(session, FIND, args)

    # log any errors
    errors = [result[1] for result in results if not result[0]]
    if len(errors) > 0:
        logger.info(errors)
        [logger.error(e) for e in errors]

    return results
