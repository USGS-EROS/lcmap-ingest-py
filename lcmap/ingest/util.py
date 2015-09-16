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


def nearest(n, mul=30, off = 0):
  """Find nearest multiple of n (with a given offset).

  This is useful for getting consistent coordinates for
  scenes that exhibit wiggle.
  """
  return round((n-off)/mul)*mul+off


def extents(path, epsg=5070):
    """
    Calculate "framing" extents for a scene.  This will give you the
    x-min, y-min, x-max, y-max values in meters relative to the origin
    of the projection (EPSG-5070 / Albers-Conus).

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


def tiles(path, **kwargs):
    """
    Returns a tile generator for the file at the given path. Each tile is
    a triple of: <col>, <row>, <data>

    This emits a structure that has tile properties (x,y,data,type) merged
    with kwargs to allow other data to be passed through. This is expected to
    be things like a scene ID, scene acquisition time (which is not included
    in a path usually), but it could theoretically be anything that can't
    be pulled from the image.

    Please note, the x and y coordinates are in terms of the projection system,
    not the grid coordinates! In other words, these are *not* from zero to
    the dimensions of the grid.

    Furthermore, we assume that a file only has one raster band for now.
    """

    grid = 100 # size in pixels, configurable maybe??
    raster = gdal.Open(path)
    for row in range(0, raster.RasterYSize, grid):
        for col in range(0, raster.RasterXSize, grid):
            yield col, row, raster.ReadAsArray(col, row, grid, grid)