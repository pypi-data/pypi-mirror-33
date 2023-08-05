"""Pre-made Dataset Provider.
"""

import pandas as pd
import tarfile
import os
from os.path import dirname, abspath

__all__ = ['init',
           'reset',
           'ls',
           'load']


def init():
    """
    Summary
    `unipy` package has some famous datasets. This function unzip the embedded
    dataset to use.
    Parameters
    ----------

    Returns
    -------
    None

    See Also
    --------
    Examples
    --------
    >>> import unipy.dataset.api as dm
    >>> dm.init()
    ['iris', 'births_small', 'anscombe', 'nutrients', 'car90', 'cars',
     'breast_cancer', 'winequality_red', 'german_credit_scoring_fars2008',
     'winequality_white', 'tips', 'air_quality', 'diabetes', 'births_big',
     'adult', 'titanic']
    """
    filepath = dirname(abspath(__file__))
    filename = filepath + '/resources.tar.gz'
    tar = tarfile.open(filename)
    filelist = list(set(map(lambda x: x.split('/')[0], tar.getnames())))
    tar.extractall(filepath)
    tar.close()
    print(filelist)


def reset():
    """
    Summary
    This function unzip the embedded dataset to use. Equal to `dm.init()`
    Parameters
    ----------

    Returns
    -------
    None

    See Also
    --------
    Examples
    --------
    >>> import unipy.dataset.api as dm
    >>> dm.reset()
    """
    filepath = dirname(abspath(__file__))
    filename = filepath + '/resources.tar.gz'
    tar = tarfile.open(filename)
    tar.extractall(filepath)
    tar.close()


def ls():
    """
    Summary
    This function shows the list of the dataset.
    Parameters
    ----------

    Returns
    -------
    list

    See Also
    --------
    Examples
    --------
    >>> import unipy.dataset.api as dm
    >>> dm.init()
    ['iris', 'births_small', 'anscombe', 'nutrients', 'car90', 'cars',
     'breast_cancer', 'winequality_red', 'german_credit_scoring_fars2008',
     'winequality_white', 'tips', 'air_quality', 'diabetes', 'births_big',
     'adult', 'titanic']
    >>> dm.ls()
    ['iris', 'births_small', 'anscombe', 'nutrients', 'car90', 'cars',
     'breast_cancer', 'winequality_red', 'german_credit_scoring_fars2008',
     'winequality_white', 'tips', 'air_quality', 'diabetes', 'births_big',
     'adult', 'titanic']
    """
    filepath = dirname(abspath(__file__))
    filename = filepath + '/resources.tar.gz'
    tar = tarfile.open(filename)
    filelist = list(set(map(lambda x: x.split('/')[0], tar.getnames())))
    dirclist = os.listdir(filepath)
    datalist = list(filter(lambda x: x in filelist, dirclist))
    datalist.sort()

    print(datalist)
    return(datalist)


def load(pick):
    """
    Summary
    This function returns a dataset you select.
    Parameters
    ----------
    pick: `str` or `int`.
        You can load a dataset by its name or its index from the list of
        `dm.ls()`. Indices start with 0.

    Returns
    -------
    pandas.DataFrame

    See Also
    --------
    Examples
    --------
    >>> import unipy.dataset.api as dm
    >>> dm.init()
    ['iris', 'births_small', 'anscombe', 'nutrients', 'car90', 'cars',
     'breast_cancer', 'winequality_red', 'german_credit_scoring_fars2008',
     'winequality_white', 'tips', 'air_quality', 'diabetes', 'births_big',
     'adult', 'titanic']
    >>> data = dm.load('anscombe')
    Dataset : anscombe
    >>> data = dm.load(2)
    Dataset : anscombe
    """
    filepath = dirname(abspath(__file__))
    dataname = pick

    if type(pick) is str:
        datafile = filepath + '/{dataset}/{dataset}.data'.format(dataset=dataname)
        data = pd.read_csv(open(datafile, 'rb'), sep=",")

    elif type(pick) is int:
        filepath = dirname(abspath(__file__))
        filename = filepath + '/resources.tar.gz'
        tar = tarfile.open(filename)
        filelist = list(set(map(lambda x: x.split('/')[0], tar.getnames())))
        dirclist = os.listdir(filepath)
        datalist = list(filter(lambda x: x in filelist, dirclist))
        datalist.sort()

        dataname = datalist[pick]
        datafile = filepath + '/{dataset}/{dataset}.data'.format(dataset=dataname)
        data = pd.read_csv(open(datafile, 'rb'), sep=",")

    print("Dataset : {}".format(dataname))
    return data
