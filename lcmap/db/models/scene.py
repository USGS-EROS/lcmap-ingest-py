""" scene.py
    ~~~~~~~~

    Scene contains data about the acquisition conditions and processing
    parameters. It is comparatively large relative to the size of a tile
    and exists to be informative. Data that is needed for a science model
    ought to be stored along with the tile to avoid excessive IO.

    Currently, a raw MTL file is stored, but certain values could be extracted
    and indexed to satisfy use cases related to inventory management. However,
    no clear use cases along those lines exist yet.

"""

from cassandra.cqlengine.named import NamedTable
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.columns import Bytes, Text, Float, Map, List, Integer, Float, DateTime


class Scene(Model):
    __table_name__ = "scenes"
    scene_name = Text(partition_key=True)
    metadata = Text()