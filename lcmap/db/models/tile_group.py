""" tile_group.py
    ~~~~~~~~~~~~~

    TileGroup provides a way to discover what layers of data are available,
    where they can be retrieved, and how they are projected and rasterized.

"""

from cassandra.cqlengine.named import NamedTable
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.columns import Bytes, Text, Float, Map, List, Integer, Float, DateTime


class TileGroup(Model):

    __table_name__ = "tile_groups"

    # One table may have many layers of harmonized data. Each layer_name is
    # a unique value, irrespective of mission. For example, "band1" won't work:
    # that covers different spectra from different instruments on different
    # satellites/platforms. Eventually, tables may contain derived ARD that
    # do not come directly from a satellite, so we can't rely on a combination
    # of satellite, instrument, and band. Having a general purpose unique
    # "layer_name" will have to do.
    table_name = Text(partition_key=True)
    layer_name = Text(primary_key=True, required=True)

    # A tile table must have all of these attributes in common, otherwise
    # data is not spatially aligned!
    projection = Text(static=True)
    tile_size = Integer(static=True, required=True)
    pixel_units = Text(static=True)
    pixel_x = Float(static=True)
    pixel_x_offset = Float(static=True)
    pixel_y = Float(static=True)
    pixel_y_offset = Float(static=True)
    resample_method = Text(static=True)

    # These are all technically optional values, but they make it much
    # easier to understand the source of data and how it can be used.
    # Yes, the data_* columns are intentionally duplicated in the tile
    # table... for now. This is a newer table, and keeping those values
    # close to the data made sense initially. I haven't decided if querying
    # this table in order to mask values is acceptable or not.
    product = Text()
    category = Text()
    long_name = Text()
    short_name = Text()
    satellite = Text()
    instrument = Text()
    spectrum = List(Float)
    data_fill = Integer()
    data_range = List(Integer)
    data_scale = Float()
    data_type = Text()
    data_units = Text()

    # This is useful for QA or mask like data. It explains how the values
    # can be used in tandem with other layers.
    class_values = Map(Integer, Text)
