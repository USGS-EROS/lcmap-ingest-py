"""
    analyze.py

    This is just an example!

"""

import time
import numpy as np
import numpy.ma as ma
import lcmap.db as db
import lcmap.models.ccdc as ccdc

import logging
logger = logging.getLogger(__name__)

def run():
    logger.info("Finding time-series")
    cube_b1, ts1 = db.search(x=-2154000, y=2049000,
        t1 = '2004-01-01', t2 = '2006-01-01',
        projection = "EPSG:5070",
        layer = "band 1 surface reflectance",
        masks = ("cloud_qa",))

    x1, x2, y1, y2 = 0, 1000, 0, 1000 # cube sample
    s1, s2 = 0, -1 # sample length (for least-squares regr)

    logger.info("Crunching numbers")
    fs = np.empty((1000,1000,4))

    for x in range(x1,x2):
        for y in range(y1,y2):
            for i, c in enumerate([cube_b1]):
                try:
                    A = ma.vstack((ts1[s1:s2], c[x][y][s1:s2])).T
                    A = ma.compress_rows(A[s1:s2])
                    coef = ccdc.simple(A)
                    fs[x][y] = np.array(coef)
                    # logger.info("<%3d,%3d>: %s" % (x,y,coef))
                except:
                    fs[x][y] = None
                    # logger.error("<%3d,%3d>: %s" % (x,y,coef))
    return fs