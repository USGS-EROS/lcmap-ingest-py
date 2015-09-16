from lcmap.db.connection import session
from lcmap import config
from datetime import datetime


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

FIND_CQL = """SELECT x, y, layer, source, acquired, data, data_type FROM epsg_5070 WHERE
    x = ? AND y = ? AND layer = ? AND acquired > ? AND acquired < ?"""

FIND = session.prepare(FIND_CQL)


def find(x, y, layer, t1, t2):
    """Find"""
    logger.debug("find <%s,%s> (%s) @ %s-%s." % (layer, x, y, t1, t2))
    t1 = datetime.strptime(t1, "%Y-%m-%d")
    t2 = datetime.strptime(t2, "%Y-%m-%d")
    parameters=(x, y, layer, t1, t2)
    results = session.execute(FIND, parameters)
    return results
