"""
   band.py
   ~~~~~~~

   Band provides access sensor data within the context of a Scene. A scene is
   necessary because emitting tiles for a band also should include extra data
   like the scene ID and acquisition time for a tile. To keep things simple,
   this metadata is included when generating tiles.

   Tile data is analysis ready: it replaces fill values with np.nan constants
   and scales values. This has not been tested extensively with other runtimes
   like Java, Matlab, Ruby, etc... but preliminary testing indicates that
   these array values translate well to other runtimes.

"""

import os
import gdal
import numpy as np

class Band:

    def __init__(self, xml, scene):
        self.xml = xml
        self.scene = scene

    #
    # Behavior for a Band that cannot be pulled directly from metadata
    #

    @property
    def path(self):
        file_name = self.xml.find("file_name").text
        return os.path.join(self.scene.dirpath, file_name)

    def tiles(self, size = 100):
        """Generate tiles (as a generator)

        Please note that the x and y properties of the yielded object are
        in projection coordinates, not raster coordinates. Refer to x_raster
        and y_raster for the column and row image coordinate values if you
        require that instead.
        """
        for row in range(0, self.raster.RasterYSize, size):
            for col in range(0, self.raster.RasterXSize, size):

                # Filter fill and out-of-range values then scale.
                data = self.raster.ReadAsArray(col, row, size, size)

                # Calculate projection system coordinates. Do not use XML
                # or MTL values: they are NOT correct!!
                # ux, uy = upper x and y
                # ox, oy = offset w-e and n-s
                # rx, ry = raster size, ignored.
                #
                # This is the right order, even though it seems strange. It is
                # expected that oy is negative... and that ux and uy are multiples
                # of the tiling grid (30*100 = strides of 3,000)
                #
                ux,ox,rx,uy,ry,oy = self.raster.GetGeoTransform()
                tx, ty = ux+col*int(ox), uy+row*int(oy)

                # Build a dict with relevant fields
                obj = dict()
                obj['x'] = int(tx)
                obj['y'] = int(ty)
                obj['layer'] = self.name
                obj['source'] = self.scene.name
                obj['acquired'] = self.scene.acquired
                obj['data'] = data
                obj['data_type'] = str(data.dtype)
                obj['data_fill'] = self.fill
                obj['data_range'] = self.valid_range
                obj['data_scale'] = self.scale
                obj['data_shape'] = data.shape
                yield obj

    @property
    def tile_count(self, size=100):
        return int((self.raster.RasterXSize/size)*(self.raster.RasterYSize/size))

    @property
    def raster(self):
        if hasattr(self, '_raster'):
            return self._raster
        else:
            self._raster = gdal.Open(self.path)
            return self._raster

    def free(self):
        """Remove raster data to reduce consumed memory.

        Bands can be several hundred megabytes and opening all of them during
        processing them can bring a memory constrained machine to it's knees.
        """
        self._raster = None

    #
    # Simple properties extracted from XML with some basic checking
    #

    @property
    def name(self):
        """Get name of this band.

        Unfortunately, the same band names aren't used for the same spectrums
        between missions. There isn't much we can do here to fix that problem,
        it's something that needs to be handled at query time.
        """
        return self.xml.get("name")

    @property
    def rows(self):
        return int(self.xml.get('nlines')),

    @property
    def cols(self):
        return int(self.xml.get('nsamps')),

    @property
    def fill(self):
        fill = self.xml.get('fill_value')
        if fill is not None:
            return int(self.xml.get('fill_value'))

    @property
    def valid_range(self):
        if not hasattr(self, '_valid_range'):
            vre = self.xml.find('valid_range')
            if vre is not None:
                min = int(vre.get('min'))
                max = int(vre.get('max'))
                self._valid_range = range(min, max)
            else:
                return None
        return (self._valid_range.start, self._valid_range.stop)

    @property
    def pixel_size(self):
        return self.xml.find('pixel_size')

    @property
    def scale(self):
        scale = self.xml.get('scale_factor')
        if scale is not None:
            return float(scale)
        else:
            return 1.0  # is this ok for a default value?
