"""
   util.py
   ~~~~~~~

   Useful functions for tile curation.

"""

import gdal
import json
import logging
import math
import numpy as np
import osr
import pyproj
import re
import subprocess


logger = logging.getLogger(__name__)
epsg_5070 = pyproj.Proj("+init=EPSG:5070")


def snap(x, y, tile_size=256, pixel_x=30, pixel_y=30, offset_x=0, offset_y=0):
    """Convert an x/y to the nearest upper left grid coordinate.

    Suppose a projection system with 30 meter pixels. If the upper-left coordinate
    for a pixel is x:45, y:50 then it has an offset_x of 15 and an offset_y of 20.

    :param x: projection system x coordinate
    :param y: projection system y coordinate
    :param tile_size: pixel width of a tile
    :param pixel_x: width of a pixel in projection system units
    :param pixel_y: height of a pixel in projection system units
    :param offset_x: e-w offset of pixel's west/left edge from projection grid
    :param offset_y: n-s offset of pixel's north/top edge from projection grid
    """
    grid_x = tile_size * pixel_x
    grid_y = tile_size * pixel_y
    sx = math.floor((x-offset_x) / grid_x) * grid_x + offset_x
    sy = math.ceil((y-offset_y) / grid_y) * grid_y + offset_y
    return sx, sy


def to_lon_lat(x, y):
    """Convert a EPSG:5070 relative x,y to lon,lat."""
    lon, lat = epsg_5070(x, y, inverse=True)
    return lon, lat


def to_epsg_5070(lon, lat):
    """Convert a lon,lat to EPSG:5070 x,y."""
    x, y = epsg_5070(lon, lat)
    return round(x), round(y)


def extents(path, epsg=5070):
    """Calculate "framing" extents for a scene.

    This returns the x-min, y-min, x-max, y-max values in meters relative
    to the origin of the projection (EPSG-5070 / Albers-Conus).

    """
    coord_ls = []

    t_ds = gdal.Open(path)
    t_band = t_ds.GetRasterBand(1)
    t_rows = t_band.YSize
    t_cols = t_band.XSize
    t_proj = t_ds.GetProjectionRef()
    t_geo = t_ds.GetGeoTransform()

    albers_proj = osr.SpatialReference()
    albers_proj.ImportFromEPSG(epsg)

    from_proj = osr.SpatialReference()
    from_proj.ImportFromWkt(t_proj)

    coord_trans = osr.CoordinateTransformation(from_proj, albers_proj)

    ll = coord_trans.TransformPoint(t_geo[0], (t_geo[3] + t_geo[5] * t_rows))
    ul = coord_trans.TransformPoint(t_geo[0], t_geo[3])
    ur = coord_trans.TransformPoint((t_geo[0] + t_geo[1] * t_cols), t_geo[3])
    lr = coord_trans.TransformPoint(
        (t_geo[0] + t_geo[1] * t_cols), (t_geo[3] + t_geo[5] * t_rows))

    x_min = min(ll[0], ul[0])
    y_min = min(ll[1], lr[1])
    x_max = max(lr[0], ur[0])
    y_max = max(ul[1], ur[1])

    i = {}
    i['x_min'] = x_min
    i['y_min'] = y_min
    i['x_max'] = x_max
    i['y_max'] = y_max

    # Determine the extents to keep consistent (xmin ymin xmax ymax)
    o = {}
    o['x_min'] = nearest(x_min - 1500, mul=3000)
    o['y_min'] = nearest(y_min - 1500, mul=3000)
    o['x_max'] = nearest(x_max + 1500, mul=3000)
    o['y_max'] = nearest(y_max + 1500, mul=3000)
    return {'extent-in': i, 'extent-out': o}


def frame(original, gx=0, gy=0, tx=256, ty=256, fill=0):
    """Surround data not aligned to the tile grid with fill data.

    This function doesn't know anything about coordinate systems. You must
    pass in raster grid upper left coordinates. See to_raster_grid() if you
    need to perform this conversion.

    :param gx: upper-left x in pixel grid coordinate space
      (**NOT** projection coordinates)
    :param gy: upper-left y in pixel grid coordinate space
      (**NOT** projection coordinates)
    :param tx: pixel width of tile
    :param ty: pixel height of tile
    :param fill: value to fill framing space
    """
    # pay special attention, the shape of the raster is (rows, cols)
    rows, cols = original.shape

    # calculate the x-offset
    x_off = abs(math.floor(gx / tx) * tx - gx)
    y_off = abs(math.floor(gy / ty) * ty - gy)

    # determine how wide the new array needs to be
    x_size = math.ceil((x_off + cols) / tx) * tx
    y_size = math.ceil((y_off + rows) / ty) * ty

    # prepare a new array that is the same type and properly filled
    framed = np.full((y_size, x_size), fill, dtype=original.dtype)

    # copy data from the original array
    framed[y_off:y_off+rows, x_off:x_off+cols] = original

    return framed

def frame_raster(raster, tile_size, fill):
    """Create a tile-grid aligned array from a GDAL raster.

    This will return an array padded with the fill value and the upper-left
    projection system coordinates of the new array.
    """
    original = np.array(raster.ReadAsArray())

    ux, ox, _, uy, _, oy = raster.GetGeoTransform()
    offset_x = ux % ox
    offset_y = uy % oy

    # The column and row of the pixel in terms of a raster grid. Suppose we
    # have 256 meter pixels projected in EPSG:5070. Every 256 meter change
    # along an axis is 1 step in the raster grid.
    gx, gy = ux / ox, uy / oy

    # Don't forget to provide fill data...
    framed = frame(original, gx, gy, tx=tile_size, ty=tile_size, fill=fill)

    # The new upper left point in the coordinate system after padding.
    cx, cy = snap(ux, uy, tile_size=tile_size,
                  pixel_x=ox, pixel_y=abs(oy),
                  offset_x=offset_x, offset_y=offset_y)

    logger.debug("reframed raster ux: {0} -> {1}, uy: {2} -> {3}".format(
        ux, cx, uy, cy))

    return framed, cx, cy

def extract_band_number(band_name):
    """Given a band name, extract the band number.

    In the ESPA XML data, the band name is an attribute of bands -> band whose
    value is of the form {product}_band{number}. This function extracts the
    value of {number} from that attribute value.
    """
    results = re.match("(?P<product>.*)_band(?P<number>\d)", "toa_band3")
    return int(results.group("number"))
