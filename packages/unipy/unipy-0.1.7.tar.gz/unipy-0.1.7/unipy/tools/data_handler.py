# -*- coding: utf-8 -*-
"""Data manipulation tools.

"""


from glob import glob
import collections
import itertools as it

import numpy as np
import pandas as pd


# Split an iterable by equal length
__all__ = ['exc',
           'splitter',
           'even_chunk',
           'pair_unique',
           'df_pair_unique',
           'map_to_tuple',
           'map_to_list',
           'merge_csv',
           'nancumsum',
           'depth',
           'zero_padder_2d',
           'zero_padder_3d']


def exc(source, blacklist):
    """Get items except the given list.

    This function splits an Iterable into the given size of multiple chunks.
    The items of An iterable should be the same type.

    Parameters
    ----------
    source: Iterable
        An Iterable to filter.

    blacklist: Iterable
        A list contains items to eliminate.

    Returns
    -------
    list
        A filtered list.

    See Also
    --------
    ``Infix Operator``

    Examples
    --------
    >>> import unipy as up
    >>> up.splitter(list(range(10)), how='equal', size=3)
    [(0, 1, 2, 3), (4, 5, 6), (7, 8, 9)]

    >>> up.splitter(list(range(10)), how='remaining', size=3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

    """
    res = [item for item in source if item not in blacklist]

    return res


# A Function to split an Iterable into smaller chunks
def splitter(iterable, how='equal', size=2):
    """Split data with given size.

    This function splits an Iterable into the given size of multiple chunks.
    The items of An iterable should be the same type.

    Parameters
    ----------
    iterable: Iterable
        An Iterable to split.

    how: {'equal', 'remaining'}
        The method to split.
        'equal' is to split chunks with the approximate length
        within the given size.
        'remaining' is to split chunks with the given size,
        and the remains are bound as the last chunk.

    size: int
        The number of chunks.

    Returns
    -------
    list
        A list of chunks.

    See Also
    --------
    numpy.array_split
    itertools.islice

    Examples
    --------
    >>> import unipy as up
    >>> up.splitter(list(range(10)), how='equal', size=3)
    [(0, 1, 2, 3), (4, 5, 6), (7, 8, 9)]

    >>> up.splitter(list(range(10)), how='remaining', size=3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

    """
    isinstance(iterable, collections.Iterable)
    isinstance(size, int)

    if not size > 0:
        raise ValueError("'size' must be greater than 0")
    else:
        if how == 'equal':
            splitted = np.array_split(iterable, (len(iterable) / size) + 1)
            resList = [tuple(chunks) for chunks in splitted]
            return resList

        elif how == 'remaining':
            tmpIterator = iter(iterable)
            splitted = iter(lambda: tuple(it.islice(tmpIterator, size)), ())
            resList = list(splitted)
            return resList


def _even_chunk(iterable, chunk_size):
    assert isinstance(iterable, collections.Iterable)
    iterator = iter(iterable)
    slicer = iter(lambda: list(it.islice(iterator, chunk_size)), [])
    yield from slicer


def _even_chunk_arr(arr, chunk_size, axis=0):
    assert isinstance(arr, np.ndarray)
    if axis in [0, 'row']:
        slicer = _even_chunk(arr, chunk_size)
    elif axis in [1, 'column']:
        slicer = _even_chunk(arr.T, chunk_size)
    return slicer


def _even_chunk_df(df, chunk_size, axis=0):
    assert isinstance(df, pd.DataFrame)
    if axis in [0, 'row']:
        colnames = df.columns
        zipped = zip(_even_chunk(df.index, chunk_size),
                     _even_chunk(df.values, chunk_size))
        slicer = (pd.DataFrame(row_arr, index=row_idx, columns=colnames)
                  for row_idx, row_arr in zipped)
    elif axis in [1, 'column']:
        rownames = df.index
        zipped = zip(_even_chunk(df.columns, chunk_size),
                     _even_chunk(df.values.T, chunk_size))
        slicer = (pd.DataFrame(col_arr, index=col_idx, columns=rownames).T
                  for col_idx, col_arr in zipped)

    yield from slicer


def _even_chunk_series(series, chunk_size):
    assert isinstance(series, pd.Series)

    name = series.name
    zipped = zip(_even_chunk(series.index, chunk_size),
                 _even_chunk(series.values, chunk_size))
    slicer = (pd.Series(val_arr, index=idx, name=name)
              for idx, val_arr in zipped)

    yield from slicer


def even_chunk(iterable, chunk_size, *args, **kwargs):
    """Split data into even size.

    This function splits an Iterable into the given size of multiple chunks.
    The items of An iterable should be the same type.

    Parameters
    ----------
    iterable: Iterable
        An Iterable to split. If N-dimensional, It is chunked by 1st dimension.

    chunk_size: ``int``
        The length of each chunks.

    Returns
    -------
    generator
        A generator yields a list of chunks. The data type of the elements
        in a list are equal to the source data type.

    See Also
    --------
    ``itertools.islice``
    ``yield from``

    Examples
    --------
    >>> import numpy as np
    >>> from unipy.tools.data_handler import even_chunk
    >>> data = list(range(7))  # list, 1D
    >>> print(data)
    [0, 1, 2, 3, 4, 5, 6]
    >>> chunked_gen = even_chunk(data, 3)
    >>> print(chunked_gen)
    <generator object even_chunk at 0x7fc4924897d8>
    >>> next(chunked_gen)
    [0, 1, 2]
    >>> chunked = list(even_chunk(data, 3))
    >>> print(chunked)
    [[0, 1, 2], [3, 4, 5], [6]]
    >>> data = np.arange(30).reshape(-1, 3)  # np.ndarray, 2D
    >>> print(data)
    array([[ 0,  1,  2],
           [ 3,  4,  5],
           [ 6,  7,  8],
           [ 9, 10, 11],
           [12, 13, 14],
           [15, 16, 17],
           [18, 19, 20],
           [21, 22, 23],
           [24, 25, 26],
           [27, 28, 29]])
    >>> chunked_gen = even_chunk(data, 4)
    >>> next(chunked_gen)
    [array([0, 1, 2]), array([3, 4, 5]), array([6, 7, 8]), array([ 9, 10, 11])]
    >>> next(chunked_gen)
    [array([12, 13, 14]),
     array([15, 16, 17]),
     array([18, 19, 20]),
     array([21, 22, 23])]
    >>> next(chunked_gen)
    [array([24, 25, 26]), array([27, 28, 29])]
    >>> next(chunked_gen)
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    StopIteration

    """
    if isinstance(iterable, np.ndarray):
        chunked = _even_chunk_arr(iterable, chunk_size, *args, **kwargs)
    elif isinstance(iterable, pd.DataFrame):
        chunked = _even_chunk_df(iterable, chunk_size, *args, **kwargs)
    elif isinstance(iterable, pd.Series):
        chunked = _even_chunk_series(iterable, chunk_size)
    else:
        chunked = _even_chunk(iterable, chunk_size)

    return chunked


def pair_unique(*args):
    """Get Unique pairsets.

    This function gets an unique pair-sets of given data.

    Parameters
    ----------
    iterable: Iterable
        Iterables having an equal length.

    Returns
    -------
    list
        A list of tuples. Each tuple is an unique pair of values.

    Raises
    ------
    ValueError
        If the lengths of argments are not equal.

    See Also
    --------
    ``zip``
    ``set``

    Examples
    --------
    >>> from unipy.tools.data_handler import pair_unique
    >>> data = dm.load('titanic')
    Dataset : titanic
    >>> data.head()
      Class     Sex    Age Survived  Freq
    0   1st    Male  Child       No     0
    1   2nd    Male  Child       No     0
    2   3rd    Male  Child       No    35
    3  Crew    Male  Child       No     0
    4   1st  Female  Child       No     0
    >>> pair_unique(data.iloc[:, 0], data.iloc[:, 1])
    [(5, '1st'), (19, '3rd'), (29, '1st'), (20, 'Crew'),
     (21, '1st'), (3, '3rd'), (16, 'Crew'), (26, '2nd'),
     (23, '3rd'), (10, '2nd'), (24, 'Crew'), (7, '3rd'),
     (4, 'Crew'), (27, '3rd'), (18, '2nd'), (28, 'Crew'),
     (30, '2nd'), (11, '3rd'), (2, '2nd'), (1, '1st'),
     (14, '2nd'), (31, '3rd'), (22, '2nd'), (17, '1st'),
     (8, 'Crew'), (9, '1st'), (32, 'Crew'), (15, '3rd'),
     (6, '2nd'), (12, 'Crew'), (13, '1st'), (25, '1st')]
    >>> idx1 = [1, 2, 3]
    >>> idx2 = [0, 9, 8, 4]
    >>> pair_unique(idx1, idx2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: All argments should have the same length.

    """
    args_tuple = (*args, )
    for x in range(len(args_tuple)):
        isinstance(x, collections.Iterable)
    len_args = [len(arg) for arg in args_tuple]
    if len(set(len_args)) != 1:
        raise ValueError('All argments should have the same length.')

    res_list = list(set(zip(*args)))

    return res_list


# Unique Pair List Creator For DataFrame
def df_pair_unique(data_frame, col_list, to_frame=False):
    """Get unique pairsets in pandas.DataFrame.

    This function gets an unique pair-sets of given columns.

    Parameters
    ----------
    data_frame: pandas.DataFrame
        DataFrame to get unique-pairs.

    col_list: pandas.Index, list, tuple
        Column names of given DataFrame.

    to_frame: Boolean (default: False)
        Choose output type.
        If True, It returns pandas.DataFrame as an output.
        If False, It returns a list of tuples.

    Returns
    -------
    list
        If to_frame=False, A list of tuples is returned.
        Each tuple is an unique pair of values.

    pandas.DataFrame
        If to_frame=True, pandas.DataFrame is returned.
        Each row is an unique pair of values.

    See Also
    --------
    pandas.DataFrame.itertuples

    Examples
    --------
    >>> from unipy.tools.data_handler import df_pair_unique
    >>> data = dm.load('titanic')
    Dataset : titanic
    >>> data.head()
      Class     Sex    Age Survived  Freq
    0   1st    Male  Child       No     0
    1   2nd    Male  Child       No     0
    2   3rd    Male  Child       No    35
    3  Crew    Male  Child       No     0
    4   1st  Female  Child       No     0
    >>> df_pair_unique(data, ['Class', 'Sex'])
    [('3rd', 'Male'), ('2nd', 'Male'), ('2nd', 'Female'), ('1st', 'Female'),
     ('Crew', 'Male'), ('1st', 'Male'), ('Crew', 'Female'), ('3rd', 'Female')]
    >>> df_pair_unique(data, ['Class', 'Sex'], to_frame=True)
      Class     Sex
    0   3rd    Male
    1   2nd    Male
    2   2nd  Female
    3   1st  Female
    4  Crew    Male
    5   1st    Male
    6  Crew  Female
    7   3rd  Female

    """
    args_tuple_map = data_frame[col_list].itertuples(index=False)
    res_list = list(set(tuple(idx) for idx in args_tuple_map))
    if to_frame:
        return pd.DataFrame(res_list, columns=col_list)
    else:
        return res_list


# %% Item Transformator
def map_to_tuple(iterable):
    """Only for some specific reason.

    """
    isinstance(iterable, collections.Iterable)
    for item in iterable:
        isinstance(item, collections.Iterator)
    res = tuple(map(lambda item: tuple(item), iterable))

    return res


def map_to_list(iterable):
    """Only for some specific reason.

    """
    isinstance(iterable, collections.Iterable)
    for item in iterable:
        isinstance(item, collections.Iterator)
    res = list(map(lambda item: tuple(item), iterable))

    return res


# %% Data Concatenator within a Folder
def merge_csv(file_path, pattern='*.csv', sep=',',
              if_save=True, save_name=None, low_memory=True):
    """Merge seperated csv type datasets into one dataset.
    Summary

    This function get separated data files together.
    When merged, the file is sorted by its name in ascending order.

    Parameters
    ----------
    file_path: str
        A directory path of source files.

    pattern: str
        A File extension with conditional naming. (default: '*.csv')

    sep: int
        A symbol seperating data columns.

    if_save: Boolean (Optional, default: True)
        False if you don't want to save the result.

    save_name: str
        A filename to save the result.
        It should be given if if_save=True.
        If inappropriate name is given, the first name of file list is used.

    low_memory: Boolean (Optional, default: True)
        It is used for pandas.read_csv() option only.

    Returns
    -------
    pandas.DataFrame
        A concatenated DataFrame.

    See Also
    --------

    Examples
    --------
    >>> from unipy.tools.data_handler import merge_csv
    >>> data = dm.load('titanic')
    Dataset : titanic
    >>> data.head(9)
      Class     Sex    Age Survived  Freq
    0   1st    Male  Child       No     0
    1   2nd    Male  Child       No     0
    2   3rd    Male  Child       No    35
    3  Crew    Male  Child       No     0
    4   1st  Female  Child       No     0
    5   2nd  Female  Child       No     0
    6   3rd  Female  Child       No    17
    7  Crew  Female  Child       No     0
    8   1st    Male  Adult       No   118
    >>> data.iloc[:2, :].to_csv('tmp1.csv', header=True, index=False)
    >>> data.iloc[2:4, :].to_csv('tmp2.csv', header=True, index=False)
    >>> data.iloc[4:9, :].to_csv('tmp3.csv', header=True, index=False)
    >>> merged = merge_csv('./')
    >>> merged
      Class     Sex    Age Survived  Freq
    0   1st    Male  Child       No     0
    1   2nd    Male  Child       No     0
    2   3rd    Male  Child       No    35
    3  Crew    Male  Child       No     0
    4   1st  Female  Child       No     0
    5   2nd  Female  Child       No     0
    6   3rd  Female  Child       No    17
    7  Crew  Female  Child       No     0
    8   1st    Male  Adult       No   118

    """
    if file_path[-1] != '/':
        file_path = file_path + '/'
    file_list = sorted(glob(file_path + pattern))

    res_frame = pd.DataFrame()
    for filename in file_list:
        file = pd.read_csv(filename, sep=sep, low_memory=low_memory)
        res_frame = res_frame.append(file, ignore_index=True)
    print('Concat Compelete.')

    if if_save:
        save_msg = "Saving it to '{save_name}'"
        if isinstance(save_name, str):
            save_name = file_path + save_name
            print(save_msg.format(save_name=save_name))
        else:
            sample_name = file_list[0].split('/')[-1]
            ext = '.' + sample_name.split('.')[-1]
            save_name = sample_name[:-(len(ext))] + '_concat' + ext
            print("'save_name' is inappropriate: '{}'".format(save_name))
            print(save_msg.format(save_name=save_name))

        res_frame.to_csv(save_name, header=True, index=False)

    return res_frame


def nancumsum(iterable):
    """A cumulative sum function.

    A cumulative sum function.

    Parameters
    ----------
    iterable: Iterable
        Iterables to calculate cumulative sum.

    Yields
    -------
    int
        A cumulative summed value.

    See Also
    --------
    numpy.isnan

    Examples
    --------
    >>> from unipy.tools.data_handler import nancumsum
    >>> tmp = [1, 2, 4]
    >>> nancumsum(tmp)
    <generator object nancumsum at 0x1084553b8>
    >>> list(nancumsum(tmp))
    [1, 3, 7]

    """
    iterator = iter(iterable)
    prev = next(iterator)
    yield prev

    for item in iterator:
        if ~np.isnan(item):
            res = prev + item
        prev = res
        yield res


def depth(iterable):
    """Get dimension depth.

    Get a dimension depth number of a nested iterable.

    Parameters
    ----------
    iterable: iterable
        An Iterable to get a dimension depth number.

    Returns
    -------
    int
        A dimension depth number.

    See Also
    --------
    collections.Iterable

    Examples
    --------
    >>> from unipy.tools.data_handler import depth
    >>> tmp = [(1, 3), (4, 6), (7, 9), (10, 12)]
    >>> depth(tmp)
    2
    >>> tmp3d = [[np.arange(i) + i for i in range(2, j)]
    ...          for j in range(5, 10)]
    >>> depth(tmp3d)
    3
    >>> # It can handle dict type (considering values only).
    >>> tmp3d_dict = [{'key' + str(i): np.arange(i) + i for i in range(2, j)}
    ...               for j in range(5, 10)]
    >>> depth(tmp3d_dict)
    3

    """
    assert isinstance(iterable, collections.Iterable), 'Not an Iterable.'
    container = iterable
    depth = 0
    while True:
        try:
            if isinstance(container, dict):
                container = iter(container.values())
            elif isinstance(container, str):
                depth += 1
                raise TypeError
            else:
                container = iter(container)
            element = next(container)
            depth += 1
            container = element

        except TypeError:
            break

    return depth


def zero_padder_2d(arr, max_len=None, method='backward'):
    """Zero-padding for fixed-length inputs(2D).

    Zero-padding Function with nested sequence.
    Each elements of a given sequence is padded fixed-length.

    Parameters
    ----------
    arr: Iterable
        A nested sequence containing 1-Dimensional numpy.ndarray.

    max_len: int (default: None)
        A required fixed-length of each sequences.
        If None, It calculates the max length of elements as max_len.

    method: {'forward', 'backward'} (default: 'backward')
        where to pad.

    Returns
    -------
    list
        A list containing 3-Dimensional numpy.ndarray with fixed-length 2D.

    See Also
    --------
    unipy.depth
    numpy.pad
    numpy.stack

    Examples
    --------
    >>> from unipy.tools.data_handler import zero_padder_2d
    >>> tmp = [np.arange(i) + i for i in range(2, 5)]
    >>> tmp
    [array([2, 3]), array([3, 4, 5]), array([4, 5, 6, 7])]
    >>> zero_padder_2d(tmp)
    array([[2, 3, 0, 0],
           [3, 4, 5, 0],
           [4, 5, 6, 7]])
    >>> zero_padder_2d(tmp, max_len=6)
    array([[2, 3, 0, 0, 0, 0],
           [3, 4, 5, 0, 0, 0],
           [4, 5, 6, 7, 0, 0]])
     >>> zero_padder_2d(tmp, max_len=5, method='forward')
    array([[0, 0, 0, 2, 3],
           [0, 0, 3, 4, 5],
           [0, 4, 5, 6, 7]])

    """
    assert isinstance(arr, collections.Iterable)
    assert all(isinstance(item, collections.Iterable) for item in arr)
    assert depth(arr) == 2, 'Not 2-Dimensional.'
    assert method in ['forward', 'backward']
    arr_max_len = max(map(len, arr))
    if max_len is None:
        max_len = arr_max_len
    else:
        assert max_len >= arr_max_len
    if method == 'forward':
        res = [np.pad(item, (max_len-len(item), 0),
                      mode='constant',
                      constant_values=0)
               for item in arr]
    elif method == 'backward':
        res = [np.pad(item, (0, max_len-len(item)),
                      mode='constant',
                      constant_values=0)
               for item in arr]
    res = np.stack(res)
    # return np.asarray(res)
    return np.stack(res)


def zero_padder_3d(arr, max_len=None, method='backward'):
    """Zero-padding for fixed-length inputs(3D).

    Zero-padding Function with nested sequence.
    Each elements of a given sequence is padded fixed-length.

    Parameters
    ----------
    arr: Iterable
        A nested sequence containing 2-Dimensional numpy.ndarray.

    max_len: int (default: None)
        A required fixed-length of each sequences.
        If None, It calculates the max length of elements as max_len.

    method: {'forward', 'backward'} (default: 'backward')
        where to pad.

    Returns
    -------
    list
        A list containing 3-Dimensional numpy.ndarray with fixed-length 2D.

    Raises
    ------
    ValueError
        All 3D shape of inner numpy.ndarray is not equal.

    See Also
    --------
    unipy.depth
    numpy.pad
    numpy.stack

    Examples
    --------
    >>> from unipy.tools.data_handler import zero_padder_3d
    >>> tmp3d = [np.arange(i * 2).reshape(-1, 2) for i in range(1, 5)]
    >>> tmp3d
    [array([[0, 1]]),
     array([[0, 1],
            [2, 3]]),
     array([[0, 1],
            [2, 3],
            [4, 5]]),
     array([[0, 1],
            [2, 3],
            [4, 5],
            [6, 7]])]
    >>> zero_padder_3d(tmp3d)
    array([[[0, 1],
            [0, 0],
            [0, 0],
            [0, 0]],

           [[0, 1],
            [2, 3],
            [0, 0],
            [0, 0]],

           [[0, 1],
            [2, 3],
            [4, 5],
            [0, 0]],

           [[0, 1],
            [2, 3],
            [4, 5],
            [6, 7]]])
    >>> tmp3d_eye
    [array([[1.]]),
     array([[1., 0.],
            [0., 1.]]),
     array([[1., 0., 0.],
            [0., 1., 0.],
            [0., 0., 1.]]),
     array([[1., 0., 0., 0.],
            [0., 1., 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.]])]
    >>> zero_padder_3d(tmp3d_eye)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 24, in zero_padder_3d
    ValueError: 3D shape should be equal.

    """
    assert isinstance(arr, collections.Iterable)
    assert all(isinstance(item, np.ndarray) for item in arr)
    assert depth(arr) == 3, 'Not 3-Dimensional.'
    assert method in ['forward', 'backward']
    arr_max_len = max(map(len, arr))
    if max_len is None:
        max_len = arr_max_len
    else:
        assert max_len >= arr_max_len
    try:
        if method == 'forward':
            res = [np.pad(item, ((max_len-len(item), 0), (0, 0)),
                          mode='constant',
                          constant_values=0)
                   for item in arr]
        elif method == 'backward':
            res = [np.pad(item, ((0, max_len-len(item)), (0, 0)),
                          mode='constant',
                          constant_values=0)
                   for item in arr]
        return np.stack(res)
    except ValueError:
        raise ValueError('3D shape should be equal.')
