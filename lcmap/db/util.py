"""
   util.py
   ~~~~~~~

   Useful functions for getting and handling database queries and results.

"""

import numpy as np
import numpy.ma as ma


def as_array(row, size=30 * 256):
    """Convert raw data into a shaped, masked, and scaled array.
    """
    arr = np.ma.frombuffer(row.data, dtype=row.data_type)
    arr = np.resize(arr, row.data_shape)
    np.ma.masked_equal(arr, row.data_fill)
    np.ma.masked_outside(arr, *row.data_range)
    arr = arr * row.data_scale
    return arr
