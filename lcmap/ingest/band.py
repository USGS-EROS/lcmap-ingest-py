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
import math
import numpy as np
import lcmap.ingest.util as util
import lcmap.ingest.errors as errors


import logging
logger = logging.getLogger(__name__)


def make_ubid(mission, product, number):
    "{}:{}:{}".format(mission, product, number)

    
class Band:

    def __init__(self, mission, product, number, scene, path, fill, valid_range,
                 scale):
        self.ubid = make_ubid(mission, product, number)
        self.scene = scene
        self.path = path
        self.fill = fill
        self.valid_range = valid_range
        self.scale = scale

    # TODO: Check pixel size and offset constraints.

    def tiles(self, tile_size, pixel_size, **kwargs):
        """Generate tiles (as a generator)

        Please note that the x and y properties of the yielded object are
        in projection coordinates, not raster coordinates. Refer to x_raster
        and y_raster for the column and row image coordinate values if you
        require that instead. We expect tiles to be square, with equally sized
        pixels in the x and y directions!

        - tile_size: the height and width of tile in pixels
        - pixel_size: the number of projection coordinate units of each pixel.
        """
        # Calculate projection system coordinates. Do not use XML
        # or MTL values: they are NOT correct!!
        # ux, uy = upper x and y
        # ox, oy = offset w-e and n-s ... unit size of pixel (e.g. 30 meters)
        # rx, ry = roation, ignored ...
        #
        # This is the right order, even though it seems strange. It is
        # expected that oy is negative... and that ux and uy are multiples
        # of the tiling grid (30*256 = strides of 7,680)
        #
        ux, ox, rx, uy, ry, oy = self.raster.GetGeoTransform()

        if self.misfit(tile_size, pixel_size):
            a, ux, uy = util.frame_raster(self.raster, tile_size, self.fill)
        else:
            a = np.array(self.raster.ReadAsArray())

        rows, cols = a.shape
        for row in range(0, rows, tile_size):
            for col in range(0, cols, tile_size):

                # Filter fill and out-of-range values then scale.
                data = a[row:row+tile_size, col:col+tile_size]

                tx, ty = ux+col*int(ox), uy+row*int(oy)

                # Build a dict with relevant fields
                obj = dict()
                obj['x'] = int(tx)
                obj['y'] = int(ty)
                # XXX this needs to be updated, now that the schema has changed
                obj['ubid'] = self.ubid
                obj['source'] = self.scene.name
                obj['acquired'] = self.scene.acquired
                obj['data'] = data
                obj['data_type'] = str(data.dtype)
                obj['data_fill'] = self.fill
                obj['data_range'] = self.valid_range
                obj['data_scale'] = self.scale
                obj['data_shape'] = data.shape
                yield obj

    def misfit(self, tile_size, pixel_size):
        """Check alignment between the raster tile grid.

        This will raise an IngestInputException if the raster pixel size and tile
        pixel size do not match or if the upper-left pixel coordinate is not a
        multiple of the tile grid's pixel size. In this case, a raster cannot be
        "framed" with not data to align it to the tile grid.

        :param tile_size: pixel width (and height)
        :type tile_size: int
        :param pixel_size: projection system units per pixel (e.g. 30 meters)
        :type pixel_size: int
        :returns: True or False
        """
        ux,ox,rx,uy,ry,oy = self.raster.GetGeoTransform()
        width, height = self.raster.RasterXSize, self.raster.RasterYSize
        grid_x = tile_size * pixel_size
        grid_y = tile_size * pixel_size
        offset_x = ux % ox
        offset_y = uy % oy

        # The pixel size of the raster must match the target's tile pixel
        # size, otherwise a tile will contain data for an area that is either
        # too big or too small.
        if (abs(ox) != pixel_size) or (abs(oy) != pixel_size):
            msg = ("band {0} input raster pixel sizes ({1},{2}) do not match "
                   "tile pixel size ({3})")
            params = (self.ubid, ox, oy, pixel_size)
            raise errors.IngestInputException(msg.format(*params))

        # The upper left of the raster must be a multiple of the pixel size
        # otherwise pixels "straddle" between two pixels on the tile grid.
        if (ux-offset_x) % pixel_size:
            msg = ("band {0} upper left x coordinate ({1}) must be an even "
                   "multiple of pixel_size ({2}+{3})")
            params = (self.ubid, ux, pixel_size, offset_x)
            raise errors.IngestInputException(msg.format(*params))

        if (uy-offset_y) % pixel_size:
            msg = ("band {0} upper left y coordinate ({1}) must be an even "
                   "multiple of pixel_size ({2}+{3})")
            params = (self.ubid, uy, pixel_size, offset_y)
            raise errors.IngestInputException(msg.format(*params))

        # If the upper-left point does not divide evenly, then it is offset.
        # Our previous tests ensure that it is safe to frame the data in order
        # to align it to the tile grid.
        if (ux % grid_x) or (uy % grid_y):
            return True

        # If the raster's width or height is different than the tile size, then
        # it is a misfit that can be fixed.
        elif (width % tile_size) or (height % tile_size):
            return True

        # if you get here, then you know the raster grid fits perfectly.
        else:
            return False

    def free(self):
        """Remove raster data to reduce consumed memory.

        Bands can be several hundred megabytes and opening all of them during
        processing them can bring a memory constrained machine to it's knees.
        """
        self._raster = None

    @property
    def tile_count(self, size=256):
        return int((self.raster.RasterXSize/size)*(self.raster.RasterYSize/size))

    @property
    def raster(self):
        if hasattr(self, '_raster'):
            return self._raster
        else:
            self._raster = gdal.Open(self.path)
            return self._raster

    #
    # Simple properties extracted from XML with some basic checking
    #

    @property
    def ubid(self):
        return self._ubid

    @ubid.setter
    def ubid(self, value):
        self._ubid = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def fill(self):
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = value

    @property
    def valid_range(self):
        if self._valid_range:
            return (self._valid_range.start, self._valid_range.stop)
        else:
            return None

    @valid_range.setter
    def valid_range(self, value):
        self._valid_range = value

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value

    @property
    def scene(self):
        return self._scene

    @scene.setter
    def scene(self, value):
        self._scene = value

    def from_xml(xml, scene):
        """Generate a Band object using metadata contained in the given xml"""

        # XXX extract mission, product, and band number info from XML
        mission = util.extract_mission_abbr(xml.find("app_version"))
        product = xml.get("product")
        number = util.extract_band_number(xml.get("name"))

        # This is the name of the band itself. Unfortunately the same name is
        # used for different spectra between missions... so we need to figure
        # out how to handle that potential problem at some point.
        #name_attr = xml.get("name")
        #if name_attr is not None:
        #    name = name_attr
        #else:
        #    name = None

        # The band is referenced in the metadata relative to whatever
        # directory contains the XML metadata. Construct a path...
        path_element = xml.find("file_name")
        if path_element is not None:
            path = os.path.join(scene.dirpath, path_element.text)
        else:
            path = None

        fill_element = xml.get('fill_value')
        if fill_element is not None:
            fill = int(xml.get('fill_value'))
        else:
            fill = None

        vr_element = xml.find('valid_range')
        if vr_element is not None:
            min = int(vr_element.get('min'))
            max = int(vr_element.get('max'))
            vr = range(min, max)
        else:
            vr = None

        scale_element = xml.get('scale_factor')
        if scale_element is not None:
            scale = float(scale_element)
        else:
            scale = None

        return Band(mission=mission, product=product, number=number,
                    scene=scene, path=path, fill=fill, valid_range=vr,
                    scale=scale)

