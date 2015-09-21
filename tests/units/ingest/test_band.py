from lcmap.ingest.band import Band
from lcmap.ingest.scene import Scene
from lcmap.ingest.errors import IngestInputException
from unittest.mock import Mock, MagicMock
import unittest
import numpy as np


class TestBand(unittest.TestCase):

    # Here we are focused on testing the tiling capability of a band object.
    # Instead of generating lots of differently sized rastes, we instead test
    # different tile sizes on the same rasters. This keeps our test data minimal
    # while verifying an important feature: varying tile sizes!
    #
    # The tests use pre-generated geotiffs with a small 5x5 raster with pixel
    # offsets (sizes) of 30. This crudely simulates the expected input to
    # the tiling system. Some of the tiles are offset by varying amounts in order
    # to facilitate different scenarios. However, we're only actually using
    # one of them to test things at the moment.

    def build_band(self, tile_path):
        scene = Mock(name="test-scene", acquired="yesterday")
        args = dict(
            path=tile_path,
            name="test-scene",
            scene=scene,
            fill=255,
            valid_range=range(-2000, 16000),
            scale=0.0001)
        return Band(**args)

    def test_aligned_tile_not_a_misfit_when_it_fits_exactly(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x_0y_30px.tif")
        self.assertFalse(band.misfit(tile_size=5, pixel_size=30))

    def test_aligned_tile_misfits_when_it_is_small(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x_0y_30px.tif")
        self.assertTrue(band.misfit(tile_size=10, pixel_size=30))

    def test_aligned_tile_misfits_when_it_is_too_big(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x_0y_30px.tif")
        self.assertTrue(band.misfit(tile_size=4, pixel_size=30))

    def test_offset_tile(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        self.assertTrue(band.misfit(tile_size=5, pixel_size=30))

    def test_offset_tile(self):
        # This IS a misfit because the tile is bigger than the
        # raster and ranges will not stride "through" a smaller
        # array.
        #
        # For example, if you walk this tile in row/column increments of 2...
        #   1,2,3
        #   4,5,6
        #   7,8,9
        # ...the 3,6,7,8,9 are lost!
        #
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        self.assertTrue(band.misfit(tile_size=10, pixel_size=30))

    def test_offset_tile_into_1x1(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        t = [t for t in band.tiles(tile_size=1, pixel_size=30)]
        self.assertEqual(len(t), 25)

    def test_offset_tile_into_2x2(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        t = [t for t in band.tiles(tile_size=2, pixel_size=30)]
        self.assertEqual(len(t), 9)

    def test_offset_tile_into_3x3(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        t = [t for t in band.tiles(tile_size=3, pixel_size=30)]
        self.assertEqual(len(t), 4)

    def test_offset_tile_into_4x4(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        t = [t for t in band.tiles(tile_size=4, pixel_size=30)]
        self.assertEqual(len(t), 4)

    def test_offset_tile_into_5x5(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        t = [t for t in band.tiles(tile_size=5, pixel_size=30)]
        self.assertEqual(len(t), 4)

    def test_offset_tile_into_10x10(self):
        band = self.build_band("tests/data/tile_5x5/offset_2x_2y_30px.tif")
        t = [t for t in band.tiles(tile_size=10, pixel_size=30)]
        self.assertEqual(len(t), 1)

    def test_aligned_tile_with_right_pixel_size(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x_0y_30px.tif")
        t = [t for t in band.tiles(tile_size=10, pixel_size=30)]
        self.assertEqual(len(t), 1)

    def test_aligned_tile_with_wrong_pixel_size(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x_0y_15px.tif")
        with self.assertRaises(IngestInputException):
            t = [t for t in band.tiles(tile_size=10, pixel_size=30)]
            self.assertEqual(len(t), 1)

    def test_aligned_tile_with_different_pixel_size(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x10_0y20_30px.tif")
        t = [t for t in band.tiles(tile_size=10, pixel_size=30, offset_x=10, offset_y=20)]
        self.assertEqual(len(t), 1)

    def test_aligned_tile_with_different_pixel_size_ux(self):
        band = self.build_band("tests/data/tile_5x5/offset_0x10_0y20_30px.tif")
        ts = [t for t in band.tiles(tile_size=2, pixel_size=30, offset_x=10, offset_y=20)]
        self.assertEqual(ts[0]['x'], 2990)
        self.assertEqual(ts[0]['y'], 2980)
        self.assertEqual(len(ts), 9)
