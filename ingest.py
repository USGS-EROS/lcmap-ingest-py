import logging
from lcmap import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)

console_handler = logging.StreamHandler()
console_handler.setLevel(config.LOG_LEVEL)
console_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s'))

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(console_handler)

import argparse
# import lcmap.ingest.envi as ingest
import lcmap.ingest.geotiff as ingest

parser = argparse.ArgumentParser()
parser.add_argument('directory', default=".")
args = parser.parse_args()

if __name__ == "__main__":
    logging.debug("Ingesting a bunch of files.")
    ingest.slurp(args.directory)
