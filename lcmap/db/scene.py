import logging
logger = logging.getLogger(__name__)


FIND = """SELECT scene_id WHERE scene_id = ?"""

SAVE = """INSERT INTO scenes (scene_id) VALUES (?)"""

def save(**kwargs):
    logger.debug("Saving scene")
    pass

def find(**kwargs):
    logger.debug("Finding scene")
    pass
