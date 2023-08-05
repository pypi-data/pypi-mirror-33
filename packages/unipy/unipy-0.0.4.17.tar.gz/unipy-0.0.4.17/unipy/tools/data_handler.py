# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 13:41:19 2017

@author: Young Ju Kim
"""


import os
import collections
import itertools as it

import numpy as np
import pandas as pd

# Split an iterable by equal length

__all__ = ['splitter',
           'even_chunk',
           'pair_unique',
           'df_pair_unique',
           'map_to_tuple',
           'map_to_list',
           'merge_csv',
           'nancumsum',
           'nancum_calculator',
           'between_generator',
           'zero_padder_3d',
           'ReusableGenerator',
           'copy_generator']


# A Function to split an Iterable into smaller chunks 
def splitter(iterable, how='equal', size=2):
    """
    Summary
    
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
    
    Examples
    --------
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
        slicer = (pd.DataFrame(row_arr, index=row_idx, columns=colnames)\
                  for row_idx, row_arr in zipped)
    elif axis in [1, 'column']:
        rownames = df.index
        zipped = zip(_even_chunk(df.columns, chunk_size),
                     _even_chunk(df.values.T, chunk_size))
        slicer = (pd.DataFrame(col_arr, index=col_idx, columns=rownames).T\
                  for col_idx, col_arr in zipped)

    yield from slicer


def _even_chunk_series(series, chunk_size):
    assert isinstance(series, pd.Series)

    name = series.name
    zipped = zip(_even_chunk(series.index, chunk_size),
                 _even_chunk(series.values, chunk_size))
    slicer = (pd.Series(val_arr, index=idx, name=name)\
              for idx, val_arr in zipped)

    yield from slicer


def even_chunk(iterable, chunk_size, *args, **kwargs):

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

    argsTuple = (*args, )

    for _ in range(len(argsTuple)):
        isinstance(_, collections.Iterable)

    resList = list(set(zip(*args)))
    
    return resList


# Unique Pair List Creator For DataFrame
def df_pair_unique(dataFrame, colList):
    
    argsTupleMap = dataFrame[colList].itertuples(index=False)
    resList = list(set(tuple(idx) for idx in argsTupleMap))
    return resList

# %% Item Transformator
def map_to_tuple(iterable):

    isinstance(iterable, collections.Iterable)
    res = tuple(map(lambda item: tuple(item), iterable))

    return res

def map_to_list(iterable):

    isinstance(iterable, collections.Iterable)
    res = list(map(lambda item: tuple(item), iterable))

    return res


# %% Data Concatenator within a Folder
def merge_csv(filePath, ext='.csv', sep=',', if_save=True, saveName=None, low_memory=True):
    if filePath[-1] != '/':
        filePath = filePath + '/'
    fileList = os.listdir(filePath)
    dataList = [name for name in fileList if name.find(ext) != -1]

    resFrame = pd.DataFrame()
    for _ in dataList:
        eachName = filePath + _
        eachFile = pd.read_csv(eachName, sep=sep, low_memory=low_memory)
        resFrame = resFrame.append(eachFile, ignore_index=True)

    if if_save == True:
        resFrame.to_csv(saveName, header=True, index=False)

    return resFrame


def nancumsum(iterable):

    iterator = iter(iterable)
    prev = next(iterator)
    yield prev

    for item in iterator:
        if ~np.isnan(item):
            res = prev + item
        prev = res
        yield res



def nancum_calculator(func):

    def nancum_generator(iterable):

        iterator = iter(iterable)
        prev = next(iterator)
        yield prev

        for item in iterator:
            if ~np.isnan(item):
                res = func(prev, item)
            prev = res
            yield res

    return nancum_generator


def between_generator(start, end, term):
    pre, nxt = start, start + term -1
    yield pre, nxt
    while nxt < end:
        pre, nxt = nxt, nxt + term
        yield pre+1, nxt


def zero_padder_3d(arr, max_len=None, method='backward'):

    
    assert isinstance(arr, collections.Iterable)
    assert all(isinstance(item, collections.Iterable) for item in arr)
    assert method in ['forward', 'backward']
    arr_max_len = max(map(len, arr))
    if not max_len:
        max_len = arr_max_len
    else:
        assert max_len >= arr_max_len
    
    if method == 'forward':
        res = [np.pad(item, ((max_len-len(item), 0), (0, 0)),
                      mode='constant',
                      constant_values=0)\
               for item in arr]

    elif method == 'backward':
        res = [np.pad(item, ((0, max_len-len(item)), (0, 0)),
                      mode='constant',
                      constant_values=0)\
               for item in arr]

    #return np.asarray(res)
    return np.stack(res)


class ReusableGenerator(object):
    def __init__(self, generator):
        self._copy(generator)

    def __iter__(self):
        self._copy(self._dummy)
        return self._source.__iter__()

    def next(self):
        if self._source == None:
            self._copy(self._dummy)
        try:
            return self._source.next()

        except StopIteration:
            self._source = None
            raise

    def _copy(self, generator):
        self._source, self._dummy = it.tee(generator)
        # self._source = (i for i in _source)
        # self._dummy = (i for i in _dummy)


def copy_generator(generator):
    _source, _dummy = it.tee(generator)
    _source = (i for i in _source)
    _dummy = (i for i in _dummy)
    return _source, _dummy

