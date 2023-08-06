"""Data manipulation tools.

This module provides a number of useful functions for data handling.

data_handler
------------
- `exc` -- Get items except the given list.
- `splitter` -- Split data with given size.
- `even_chunk` -- Split data into even size.
- `pair_unique` -- Get Unique pairsets.
- `df_pair_unique` -- Get unique pairsets in pandas.DataFrame.
- `merge_csv` -- Merge seperated csv type datasets into one dataset.
- `nancumsum` -- A cumulative sum function.
- `depth` -- Get dimension depth.
- `zero_padder_2d` -- Zero-padding for fixed-length inputs(2D).
- `zero_padder_3d` -- Zero-padding for fixed-length inputs(3D).

"""


from unipy.tools import data_handler

from unipy.tools.data_handler import *


__all__ = []
__all__ += data_handler.__all__
