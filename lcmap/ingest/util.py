""" Useful functions for tile curators.
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

    t_ds   = gdal.Open(path)
    t_band = t_ds.GetRasterBand(1)
    t_rows = t_band.YSize
    t_cols = t_band.XSize
    t_proj = t_ds.GetProjectionRef()
    t_geo  = t_ds.GetGeoTransform()

    albers_proj = osr.SpatialReference()
    albers_proj.ImportFromEPSG(epsg)

    from_proj = osr.SpatialReference()
    from_proj.ImportFromWkt(t_proj)

    coord_trans = osr.CoordinateTransformation(from_proj, albers_proj)

    ll = coord_trans.TransformPoint(t_geo[0], (t_geo[3] + t_geo[5] * t_rows))
    ul = coord_trans.TransformPoint(t_geo[0], t_geo[3])
    ur = coord_trans.TransformPoint((t_geo[0] + t_geo[1] * t_cols), t_geo[3])
    lr = coord_trans.TransformPoint((t_geo[0] + t_geo[1] * t_cols), (t_geo[3] + t_geo[5] * t_rows))

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
    o['x_min'] = nearest(x_min-1500, mul=3000)
    o['y_min'] = nearest(y_min-1500, mul=3000)
    o['x_max'] = nearest(x_max+1500, mul=3000)
    o['y_max'] = nearest(y_max+1500, mul=3000)
    return {'extent-in': i, 'extent-out': o}

# python exents.py LC80440332015128LGN00/LC80440332015128LGN00_B1.TIF

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('src', help='source input (a geotiff)')
args = vars(parser.parse_args())

extent = extents(args['src'])
print(args['src'])
print(json.dumps(extent,sort_keys=True, indent=4))
