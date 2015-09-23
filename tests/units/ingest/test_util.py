import unittest
import numpy as np
import lcmap.ingest.util as u


class TestUtil(unittest.TestCase):

    # Hi! Yes, these tests are somewhat repetitive, but there are a number
    # of variations that need to be accounted for when framing data. I was
    # tempted to move the last part of the framing tests into it's own function
    # but then I'd have to test-the-tests... ;)


    #
    # Snapping y-coordinate test
    #

    def test_snap_y_simple(self):
        x, y = u.snap(0, 0)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_snap_y_simple_02(self):
        x, y = u.snap(0, 1500)
        self.assertEqual(x, 0)
        self.assertEqual(y, 3000)

    def test_snap_y_simple_03(self):
        x, y = u.snap(0, 3456)
        self.assertEqual(x, 0)
        self.assertEqual(y, 6000)

    def test_snap_y_simple_04(self):
        x, y = u.snap(0, -1500)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_snap_y_simple_05(self):
        x, y = u.snap(0, -3456)
        self.assertEqual(x, 0)
        self.assertEqual(y, -3000)

    def test_snap_y_offset_01(self):
        x, y = u.snap(0, 9, offset_y=10)
        self.assertEqual(x, 0)
        self.assertEqual(y, 10)

    def test_snap_y_offset_02(self):
        x, y = u.snap(0, 10, offset_y=10)
        self.assertEqual(x, 0)
        self.assertEqual(y, 3010)

    def test_snap_y_offset_02(self):
        x, y = u.snap(0, 11, offset_y=10)
        self.assertEqual(x, 0)
        self.assertEqual(y, 3010)

    def test_snap_y_offset_03(self):
        x, y = u.snap(0, 500, offset_y=100)
        self.assertEqual(x, 0)
        self.assertEqual(y, 3100)

    #
    # Snapping x-coordinate test
    #

    def test_snap_x_simple(self):
        x, y = u.snap(0, 0)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_snap_x_simple_02(self):
        x, y = u.snap(1500, 0)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_snap_x_simple_03(self):
        x, y = u.snap(3500, 0)
        self.assertEqual(x, 3000)
        self.assertEqual(y, 0)

    def test_snap_x_simple_04(self):
        x, y = u.snap(-1500, 0)
        self.assertEqual(x, -3000)
        self.assertEqual(y, 0)

    def test_snap_x_offset_01(self):
        x, y = u.snap(0, 0, offset_x=10)
        self.assertEqual(x, -2990)
        self.assertEqual(y, 0)

    def test_snap_x_offset_02(self):
        x, y = u.snap(3000, 3000, offset_x=-10)
        self.assertEqual(x,  2990)
        self.assertEqual(y,  3000)

    def test_snap_x_offset_03(self):
        x, y = u.snap(11, 0, offset_x=10)
        self.assertEqual(x, 10)
        self.assertEqual(y, 0)

    def test_snap_x_offset_04(self):
        x, y = u.snap(500, 0, offset_x=100)
        self.assertEqual(x, 100)
        self.assertEqual(y, 0)

    def test_snap_realistic(self):
        x, y = u.snap(-2264999, 3128999)
        self.assertEqual(x, -2265000)
        self.assertEqual(y,  3129000)

    def test_snap_with_offset(self):
        x, y = u.snap(-2265000, 3129000, offset_y=10)
        self.assertEqual(x, -2265000)
        self.assertEqual(y,  3129010)

    def test_frame_small_fits_in_one_tile(self):
        """Array is too small but fits entirely in one tile."""
        a = np.array(range(1, 10))
        a.resize((3, 3))  # 3x3 grid

        expected_shape = (5, 5)
        expected_fills = 5 * 5 - 9
        expected_value = 9

        f = u.frame(a, gx=1, gy=1, tx=5, ty=5, fill=255)
        self.assertEqual(f.shape, expected_shape)
        self.assertEqual(np.count_nonzero(f == 255), expected_fills)
        self.assertEqual(np.count_nonzero(f < 255), expected_value)

    def test_frame_small_spans_across_two_tiles(self):
        """Array is too small but spans two tiles."""
        a = np.array(range(1, 10))
        a.resize((3, 3))

        expected_shape = (5, 10)
        expected_fills = 5 * 10 - 9
        expected_value = 9

        f = u.frame(a, gx=-1, gy=1, tx=5, ty=5, fill=255)
        self.assertEqual(f.shape, expected_shape)
        self.assertEqual(np.count_nonzero(f == 255), expected_fills)
        self.assertEqual(np.count_nonzero(f < 255), expected_value)

    def test_frame_small_spans_across_four_tiles(self):
        """Array is too small but spans four tiles."""
        a = np.array(range(1, 10))
        a.resize((3, 3))

        expected_shape = (10, 10)
        expected_fills = 10 * 10 - a.size
        expected_value = a.size

        f = u.frame(a, gx=-1, gy=-1, tx=5, ty=5, fill=255)
        self.assertEqual(f.shape, expected_shape)
        self.assertEqual(np.count_nonzero(f == 255), expected_fills)
        self.assertEqual(np.count_nonzero(f < 255), expected_value)

    def test_frame_big_spans_across_two_tiles(self):
        """Array is tile-aligned an spans two tiles exactly."""
        a = np.array(range(1, 50))
        a.resize((10, 5))

        expected_shape = (10, 5)
        expected_fills = 10 * 5 - a.size
        expected_value = a.size

        f = u.frame(a, gx=0, gy=0, tx=5, ty=5, fill=255)
        self.assertEqual(f.shape, expected_shape)
        self.assertEqual(np.count_nonzero(f == 255), expected_fills)
        self.assertEqual(np.count_nonzero(f < 255), expected_value)

    def test_frame_big_spans_across_four_tiles(self):
        """Array is tile-aligned but spans four tiles."""
        a = np.array(range(1, 36))
        a.resize((6, 6))

        expected_shape = (10, 10)
        expected_fills = 10 * 10 - a.size
        expected_value = a.size

        f = u.frame(a, gx=0, gy=0, tx=5, ty=5, fill=255)
        self.assertEqual(f.shape, expected_shape)
        self.assertEqual(np.count_nonzero(f == 255), expected_fills)
        self.assertEqual(np.count_nonzero(f < 255), expected_value)

    def test_frame_big_spans_across_nine_tiles(self):
        """Array is big an is not aligned so it spans nine tiles."""
        a = np.array(range(1, 64))
        a.resize((8, 8))

        expected_shape = (15, 15)
        expected_fills = 15 * 15 - a.size
        expected_value = a.size

        f = u.frame(a, gx=3, gy=3, tx=5, ty=5, fill=255)
        self.assertEqual(f.shape, expected_shape)
        self.assertEqual(np.count_nonzero(f == 255), expected_fills)
        self.assertEqual(np.count_nonzero(f < 255), expected_value)
