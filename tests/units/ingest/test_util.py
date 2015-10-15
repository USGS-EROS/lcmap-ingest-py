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
        self.assertEqual(y, 7680)

    def test_snap_y_simple_03(self):
        x, y = u.snap(0, 8000)
        self.assertEqual(x, 0)
        self.assertEqual(y, 15360)
        x, y = u.snap(0, -8000)
        self.assertEqual(x, 0)
        self.assertEqual(y, -7680)

    def test_snap_y_simple_04(self):
        x, y = u.snap(0, -1500)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_snap_y_simple_05(self):
        x, y = u.snap(0, -16000)
        # XXX I need some convincing here ... -15000 and -8000 both snap to
        # -7680, and I think this behaviour might be different than the
        # positive numbers. Will talk with Jon about this the next time I'm in
        # the office. I may just need to get an update on how snapping is
        # intended to work (i.e., there may not actually be a problem here).
        self.assertEqual(x, 0)
        self.assertEqual(y, -15360)

    def test_snap_y_offset_01(self):
        x, y = u.snap(0, 9, offset_y=10)
        self.assertEqual(x, 0)
        self.assertEqual(y, 10)

    def test_snap_y_offset_02(self):
        x, y = u.snap(0, 10, offset_y=10)
        self.assertEqual(x, 0)
        self.assertEqual(y, 7690)

    def test_snap_y_offset_02(self):
        x, y = u.snap(0, 11, offset_y=10)
        self.assertEqual(x, 0)
        self.assertEqual(y, 7690)

    def test_snap_y_offset_03(self):
        x, y = u.snap(0, 500, offset_y=256)
        self.assertEqual(x, 0)
        self.assertEqual(y, 7936)

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
        x, y = u.snap(-1500, 0)
        self.assertEqual(x, -7680)
        self.assertEqual(y, 0)

    def test_snap_x_simple_03(self):
        x, y = u.snap(8000, 0)
        self.assertEqual(x, 7680)
        self.assertEqual(y, 0)
        x, y = u.snap(-8000, 0)
        self.assertEqual(x, -15360)
        self.assertEqual(y, 0)

    def test_snap_x_simple_04(self):
        x, y = u.snap(-1500, 0)
        self.assertEqual(x, -7680)
        self.assertEqual(y, 0)

    def test_snap_x_offset_01(self):
        x, y = u.snap(0, 0, offset_x=10)
        self.assertEqual(x, -7670)
        self.assertEqual(y, 0)

    def test_snap_x_offset_02(self):
        x, y = u.snap(7680, 7680, offset_x=-10)
        self.assertEqual(x,  7670)
        self.assertEqual(y,  7680)

    def test_snap_x_offset_03(self):
        x, y = u.snap(11, 0, offset_x=10)
        self.assertEqual(x, 10)
        self.assertEqual(y, 0)

    def test_snap_x_offset_04(self):
        x, y = u.snap(500, 0, offset_x=256)
        self.assertEqual(x, 256)
        self.assertEqual(y, 0)

    def test_snap_realistic(self):
        x, y = u.snap(-2264999, 3128999)
        self.assertEqual(x, -2265600)
        self.assertEqual(y,  3133440)

    def test_snap_with_offset(self):
        x, y = u.snap(-2264999, 3128999, offset_y=10)
        self.assertEqual(x, -2265600)
        self.assertEqual(y,  3133450)

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
