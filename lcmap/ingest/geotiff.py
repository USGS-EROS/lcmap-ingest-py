import pathlib
import numpy as np
import time
import os
import gdal
import math
import glob
import logging
import json
import lcmap.ingest.metadata as meta
from lcmap.ingest import util
from multiprocessing import Pool
from lcmap.db import cassandra
from lcmap import config
from cassandra.concurrent import execute_concurrent_with_args

logger = logging.getLogger()


def slurp(where='.'):
    with IngestManager() as manager:
        here = pathlib.Path(where)
        paths = list(here.glob('**/*.tar.gz'))
        logger.debug(paths)
        logger.info('number of files found: {0}'.format(len(paths)))
        manager.ingest_files(paths)


def ingest_file(path):
    # extract the compressed files
    logger.info('decompressing {0}'.format(path))
    basedir = util.decompress(str(path))
    # search for the metadata file in the extracted directory
    metadata_paths = list(glob.glob(os.path.join(basedir, '*.xml')))
    logger.info('metadata_paths: {0}'.format(metadata_paths))
    for metadata_path in metadata_paths:
        # should only be one metadata file
        logger.info('parsing metadata {0}'.format(metadata_path))
        start_time = time.time()
        metadata = meta.parse(str(metadata_path))
        for band in metadata['bands']:
            start_time = time.time()
            ingest_band(band, metadata)
            logger.info('ingest band {0} took {1}'.format(os.path.basename(band['file_path']), time.time() - start_time))

        logger.info('ingest image {0} took {1}'.format(str(metadata_path), time.time() - start_time))

    # clean up the decompressed directory
    util.rmdir(basedir)


def ingest_band(band, metadata, size=config.TILE_SIZE):
    """
    Take a large array and tile it into smaller ones.

    This is not very configurable yet, but eventually you will be able
    to control tile size, read projection and pixel size.

    Since we're not saving anywhere else, it doesn't make sense
    to extract the save function into something more generic -- we're
    really just focused on Cassandra for now.
    """

    # extract details about the band
    layer = band['name']
    logger.info('ingesting band {0}'.format(layer))
    logger.debug(band)

    # extract details from the metadata
    info = metadata['info']
    logger.debug(info)
    satellite = info['satellite']
    instrument = info['instrument']
    x = math.floor(info['extent']['ul']['x'])
    y = math.floor(info['extent']['ul']['y'])
    acquisition_date = info['acquisition_date']

    # open the image file and get the raster band
    img = gdal.Open(band['file_path'])
    raster = img.GetRasterBand(1)

    tiles = []
    for row in range(0, band['rows'], size):
        for col in range(0, band['cols'], size):
            logger.debug('layer: {0}, row: {1}, col: {2}'.format(layer, row, col))

            # calculate the extent to work with for a row/column
            ex = x + col * band['pixel_size']['x']
            ey = y + row * band['pixel_size']['y']
            logger.debug('ex: {0}, ey: {1}'.format(ex, ey))

            # read the data for the extent
            img_data = raster.ReadAsArray(row, col, size, size).astype(np.float64)

            # determine the elements with either fill values or out of range values
            logger.debug('scaling and masking image data')
            if 'fill_value' in band:
                img_data[img_data == band['fill_value']] = np.nan
            if 'valid_range' in band:
                img_data[img_data < band['valid_range']['min']] = np.nan
                img_data[img_data > band['valid_range']['max']]

            # apply a scale factor to the remaining data if a scale factor was specified
            if 'scale_factor' in band:
                img_data = img_data * band['scale_factor']

            # save the data if there is anything left after masking
            if np.all(np.isnan(img_data)):
                logger.debug('skip {0}:<{1},{2}>@{3} (entirely no data)'.format(layer, ex, ey, acquisition_date))
                pass
            else:
                logger.debug('save {0}:<{1},{2}>@{3}'.format(layer, ex, ey, acquisition_date))
                tiles.append([ex, ey, satellite, instrument, layer, acquisition_date, json.dumps(band), img_data])

    # ingest all of the tiles for this band
    IngestManager.ingest(tiles)


class IngestManager(object):

    concurrency = config.CASSANDRA_QUERY_CONCURRENCY

    def __init__(self, process_count=config.PROCESS_COUNT):
        cluster = cassandra.get_cluster()
        self.pool = Pool(processes=process_count, initializer=self._setup, initargs=(cluster, config.CASSANDRA_KEYSPACE,))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.pool.close()
        self.pool.join()

    def ingest_files(self, paths):
        results = [self.pool.apply_async(ingest_file, args=(path,)) for path in paths]
        [p.get() for p in results]

    @classmethod
    def _setup(cls, cluster, keyspace):
        cls.session = cassandra.get_session(cluster)
        cls.insert = cassandra.prepare_insert(cls.session)

    @classmethod
    def ingest(cls, tiles):
        execute_concurrent_with_args(cls.session, cls.insert, tiles)
