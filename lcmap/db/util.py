"""
   util.py
   ~~~~~~~

   Useful functions for getting and handling database queries and results.

"""

import numpy as np
import numpy.ma as ma
import pandas as pd

import logging
logger = logging.getLogger(__name__)


def as_array(row, size=30 * 100):
    """Convert raw data into a shaped, masked, and scaled array.
    """
    arr = np.ma.frombuffer(row.data, dtype=row.data_type)
    arr = np.resize(arr, row.data_shape)
    np.ma.masked_equal(arr, row.data_fill)
    np.ma.masked_outside(arr, *row.data_range)
    arr = arr * row.data_scale
    return arr


def meld(cube, grid=30 * 100):

    # trim out statements that did not return anything and reshape to only return the data rows
    rows = [row for result in cube if result[0] and len(result[1]) > 0 for row in result[1]]

    # convert the data arrays to something we can use (i.e. shaped, masked, and scaled)
    tiles = []
    for row in rows:
        tile = row._asdict()
        tile['data'] = as_array(row)
        tiles.append(tile)

    """
    Take the original structure

      x, y, layer, acquired, data

    and merge the data arrays it to this structure

      acquired, layer, data

    """

    # create a dataframe to make it easier to select from the tiles
    df_in = pd.DataFrame(tiles)
    if df_in.empty:
        return

    # get each of the unique gropus for the resulting dataframe
    grouped = [{'acquired': key[0], 'layer': key[1]} for key, group in df_in.groupby(['acquired', 'layer'])]

    # iterate over the groups and accumulate the result
    result = []
    for group in grouped:

        # select all of the source rows for the group
        source = df_in[(df_in.acquired == group['acquired']) & (df_in.layer == group['layer'])]

        # stack the arrays horizontally and vertically
        ys = source.y.unique()
        y_data = np.vstack([np.hstack(source[source.y == y].data) for y in ys])

        # save the data to the group
        group['data'] = y_data

        # append the group to the result
        result.append(group)

    # create a dataframe with the results so it's easier to select a portion of the data
    df = pd.DataFrame(result)
    return df.set_index(['acquired', 'layer'])
