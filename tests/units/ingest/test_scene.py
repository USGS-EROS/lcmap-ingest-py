from lcmap.ingest.scene import Scene
from unittest.mock import MagicMock
from datetime import datetime
import unittest

class TestScene(unittest.TestCase):

    # These tests use metadata exported from ESPA, but they exclude the
    # band data because even a small number of bands can get large and
    # the repository should stay small.

    def test_real(self):
        s = Scene("tests/data/scenes/LC80440342015176")
        self.assertIsNotNone(s.acquired)
        self.assertIsInstance(s.acquired, datetime)

    def test_scene_name(self):
        s = Scene("tests/data/scenes/LC80440342015176")
        self.assertEqual(s.name, "LC80440342015176LGN00")

    def test_scene_name(self):
        s = Scene("tests/data/scenes/LC80440342015176")
        self.assertEqual(s.name, "LC80440342015176LGN00")

    def test_band_count(self):
        s = Scene("tests/data/scenes/LC80440342015176")
        b = [b for b in s.bands]
        b1 = s.bands[0]
        self.assertEqual(len(b), 20)
        self.assertEqual(b1.path, "tests/data/scenes/LC80440342015176/LC80440342015176LGN00_toa_band1.tif")
        self.assertEqual(b1.fill,   -9999)
        self.assertEqual(b1.scale, 0.0001)
        self.assertEqual(b1.valid_range, (-2000, 16000))
