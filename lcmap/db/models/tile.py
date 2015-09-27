""" tile.py
    ~~~~~~~

    Tile is essentially a base class.

    Although tiles are similarly structured,different projection and raster
    schemes imply a need for separate tables; only data that is completely
    harmonized should co-exist in a single table.

    The base class implements the following common behaviors:

    1. Find. The class exposes a method that relies on projection and raster
       parameters to snap arbitrary coordinates to the containing tile.

    2. Save. A function that provides validation and prevents data that is not
       aligned the tile grid or projection system from being added to the
       collection.

    3. Data conversion. A function that transforms raw binary data to a shaped,
       scaled, and masked array.

"""

from cassandra.cqlengine.named import NamedTable
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.columns import Bytes, Text, Float, Map, List, Integer, Float, DateTime
from cassandra.cqlengine.management import sync_table
from lcmap.db.models.tile_group import TileGroup
from lcmap.ingest.util import snap
from datetime import datetime

import numpy as np


class Tile(Model):

    """This is intended to be inherrited from. Don't store data here."""

    # add validation for this class that must be overriden to prevent
    # saving to this table.

    __table_name__ = "tiles"

    x = Integer(partition_key=True)
    y = Integer(partition_key=True)
    layer = Text(partition_key=True, index=True)
    acquired = DateTime(primary_key=True, clustering_order='DESC')
    source = Text(index=True)

    data = Bytes(required=True, static=True)
    data_type = Text(required=True, static=True)
    data_shape = List(Integer, required=True, static=True)
    data_scale = Float(static=True)
    data_range = List(Integer, static=True)
    data_fill = Integer(static=True)

    @property
    def array(self):
        """Build an array from raw data.

        Array is shaped, scaled, and masked using range and fill values
        if they exist. The array is memoized to improve performance."""

        if not hasattr(self, '_array'):

            # It's possible to query the table in a way that returns fewer
            # columns. If the data column was not included, we cannot build
            # an array! Even if data is included, we need the type too, so
            # verify both are present.
            if self.data and self.data_type:
                a = np.ma.frombuffer(self.data, dtype=self.data_type)
            else:
                return None

            if self.data_shape:
                a = np.resize(a, self.data_shape)
            if self.data_fill:
                np.ma.masked_equal(a, self.data_fill)
            if self.data_range:
                np.ma.masked_outside(a, *self.data_range)
            if self.data_scale:
                a = a * self.data_scale
            self._array = a

        return self._array

    @property
    def scene(self):
        """Get information about source scene of this tile."""
        if not hasattr(self, '_scene'):
            # find the scene
            self._scene = s
        return self._scene

    @classmethod
    def get_tile_table(self):
        """Get information about tiles this table may contain."""
        if not hasattr(self, '_tile_table'):
            q = TileGroup.objects.filter(
                TileGroup.table_name == self.__table_name__)
            layers = q.all()
            self._tile_table = list(layers)

        # what if there are no layers, raise an exception maybe?

        return self._tile_table

    @classmethod
    def snap(self, x, y):
        tt = self.get_tile_table()[0]
        return snap(x, y, tile_size=tt.tile_size,
                    pixel_x=tt.pixel_x,
                    pixel_y=tt.pixel_y,
                    offset_x=tt.pixel_x_offset,
                    offset_y=tt.pixel_y_offset)

    @classmethod
    def find(self, x, y, layer, **kwargs):
        # use the tile table configuration to specify parameters
        new_x, new_y = self.snap(x, y)
        q = self.objects(self.x == new_x, self.y == new_y, self.layer == layer)
        if 't1' in kwargs:
            t1 = datetime.strptime(kwargs['t1'], "%Y-%m-%d")
            q = q.filter(self.acquired > t1)
        if 't2' in kwargs:
            t2 = datetime.strptime(kwargs['t2'], "%Y-%m-%d")
            q = q.filter(self.acquired < t2)
        return q

    @classmethod
    def save(self, **kwargs):
        return "saving stuff for {0} with {1}".format(self.__table_name__, kwargs)


class CONUS(Tile):
    __table_name__ = "epsg_5070"


class Alaska(Tile):
    __table_name__ = "epsg_3338"
