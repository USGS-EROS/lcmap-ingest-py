import logging
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

root = logging.getLogger()
root.setLevel(logging.DEBUG)

import argparse
import lcmap.ingest.envi as e

parser = argparse.ArgumentParser()
parser.add_argument('directory', default=".")
args = parser.parse_args()

if __name__ == "__main__":
    logging.debug("Ingesting a bunch of files.")
    e.slurp(args.directory)

