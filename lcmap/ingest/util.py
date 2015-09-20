"""
   util.py
   ~~~~~~~

   Useful functions for tile curation.

"""

import gdal
import osr
import math
import subprocess
import json
import pyproj
import math
import numpy as np


epsg_5070 = pyproj.Proj("+init=EPSG:5070")


def snap(x, y, tile_size=100, pixel_x=30, pixel_y=30):
    """Convert an x/y to the nearest grid coordinate."""
    grid_x = tile_size * pixel_x
    grid_y = tile_size * pixel_y
    sx = math.floor(x / grid_x) * grid_x
    sy = math.ceil(y / grid_x) * grid_y
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


def frame(original, ux=0, uy=0, tx=100, ty=100, fill=0):
    """Surround data not aligned to the tile grid with fill data.

    This function doesn't know anything about coordinate systems. You must
    pass in raster grid upper left coordinates. See to_raster_grid() if you
    need to perform this conversion.

    ux upper-left x in pixel grid coordinate space (**NOT** projection coordinates)
    uy upper-left y in pixel grid coordinate space (**NOT** projection coordinates)
    tx pixel width of tile
    ty pixel height of tile
    """
    ow, oh = original.shape

    # calculate the x-offset
    x_off = abs(math.floor(ux / tx) * tx - ux)
    y_off = abs(math.floor(uy / ty) * ty - uy)
    # print(x_off,ow,y_off,oh)

    # determine how wide the new array needs to be
    # bug. wrong.
    x_size = math.ceil((x_off + ow) / tx) * tx
    y_size = math.ceil((y_off + oh) / ty) * ty

    # prepare a new array that is the same type and properly filled
    framed = np.full((x_size, y_size), fill, dtype=original.dtype)

    # copy data from the original array
    framed[x_off:x_off+ow, y_off:y_off+oh] = original

    return framed


def frame_raster(raster, tile_size, fill):
    """Create a tile-grid aligned array from a GDAL raster.

    This will return an array padded with the fill value and the upper-left
    projection system coordinates of the new array.
    """
    original = np.array(raster.ReadAsArray())

    ux, ox, _, uy, _, oy = raster.GetGeoTransform()

    # The column and row of the pixel in terms of a raster grid. Suppose we
    # have 100 meter pixels projected in EPSG:5070. Every 100 meter change
    # along an axis is 1 step in the raster grid.
    rx, ry = int(ux / ox), int(uy / oy)

    # Don't forget to provide fill data...
    framed = frame(original, rx, ry, tx=tile_size, ty=tile_size, fill=fill)

    # The new upper left point in the coordinate system after padding.
    cx, cy = snap(ux, uy, tile_size=tile_size,  pixel_x=ox, pixel_y=oy)

    return framed, cx, cy
