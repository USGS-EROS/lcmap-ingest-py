import pathlib
import spectral
import datetime
import numpy as np
import re
from lcmap.db.cassandra import save


def slurp(where="."):
    here = pathlib.Path(where)
    paths = list(here.glob("**/*.hdr"))
    for path in paths:
        logger.info('ingesting %s', path)
        img = spectral.open_image(str(path))
        ingest(img)


def ingest(img, size = 100, res = 30):
    """
    Take a large array and tile it into smaller ones.

    This is not very configurable yet, but eventually you will be able
    to control tile size, read projection and pixel size.

    Since we're not saving anywhere else, it doesn't make sense
    to extract the save function into something more generic -- we're
    really just focused on Cassandra for now.
    """
    pattern = "(L[CE][0-9])([0-9]{3})([0-9]{3})([0-9]{7}).+"
    m = re.search(pattern, img.filename)
    mission, path, row, collect = m.groups()
    time = datetime.datetime.strptime(collect, "%Y%j")
    layer = img.metadata['band names'][0]
    x = int(img.metadata['map info'][3])
    y = int(img.metadata['map info'][4])
    proj = "EPSG:5070" # TODO: read from file??

    if img.metadata.get('data ignore value'):
        ignore = int(img.metadata.get('data ignore value'))
    else:
        ignore = None

    logger.info('image metadata parsed')

    for row in range(0, img.nrows, size):
        logger.debug('layer: %s row: %s', layer, row)
        for col in range(0, img.ncols, size):
            data = img.read_subregion((row, row + size), (col, col + size))
            ex = x + col * res
            ey = y + row * res
            if ignore:
                if not np.all(data == ignore):
                    save(proj, ex, ey, mission, None, layer, time, data)
                    #logger.debug('save %s:<%s,%s>@%s', layer, ex, ey, time)
                else:
                    pass
                    #logger.debug('skip %s:<%s,%s>@%s (entirely no data)', layer, ex, ey, time)
            else:
                logger.debug('save %s:<%s,%s>@%s', layer, ex, ey, time)
                save(proj, ex, ey, mission, None, layer, time, data)


import logging
logger = logging.getLogger(__name__)