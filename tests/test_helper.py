"""Test Helper

   This module contains functions that support automated testing.


"""

import gdal, osr, os
import numpy as np


def create(loc, a, off_x, off_y, pixel_size = 30):
    width, height = a.shape
    driver = gdal.GetDriverByName('GTiff')
    raster = driver.Create(loc, width, height, 1, gdal.GDT_Byte)
    raster.SetGeoTransform((off_x, pixel_size, 0, off_y, 0, -pixel_size))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(5070)
    raster.SetProjection(srs.ExportToWkt())
    band = raster.GetRasterBand(1)
    band.WriteArray(a)
    band.FlushCache()


def make_geotiffs():

    # We are assuming the tile grid points are evenly spaced multiples of 30
    # and 256.
    tile_grid = 30 * 256

    # ...but we are going to create a relatively small tile. This will exercise
    # filling data around an entire tile.
    a = np.array(range(0,25))
    a = a.reshape(5,5)

    # this tiff is aligned to the grid
    create("tests/data/tile_5x5/offset_0x_0y_30px.tif", a, -tile_grid*5,
            tile_grid*8)

    # this tiff is 2 grid-units below and to the right from the nearest tile.
    create("tests/data/tile_5x5/offset_2x_2y_30px.tif", a, tile_grid+60,
            tile_grid-60)

    # this tiff is 3 grid units off along the x axis and 0 units off along the
    # y axis.
    create("tests/data/tile_5x5/offset_3x_0y_30px.tif", a, tile_grid+90,
            tile_grid)

    # this tiff is 0 grid units off along the x axis and 3 units off along the
    # y axis.
    create("tests/data/tile_5x5/offset_0x_3y_30px.tif", a, tile_grid+90,
            tile_grid)

    # this tiff is 0 grid units off along the x axis and 3 units off along the
    # y axis.
    create("tests/data/tile_5x5/offset_0x_0y_15px.tif", a, tile_grid,
            tile_grid, 15)

    # this tiff is 0 grid units off along the x axis and 3 units off along the
    # y axis.
    create("tests/data/tile_5x5/offset_0x10_0y20_30px.tif", a, tile_grid+10,
            tile_grid+20, 30)

make_geotiffs()
