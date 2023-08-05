# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 05:03:19 2017

@author: Young Ju Kim
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
    filepath = dirname(abspath(__file__))
    filename = filepath + '/resources.tar.gz'
    tar = tarfile.open(filename)
    filelist = list(set(map(lambda x: x.split('/')[0], tar.getnames())))
    tar.extractall(filepath)
    tar.close()
    print(filelist)


def reset():
    filepath = dirname(abspath(__file__))
    filename = filepath + '/resources.tar.gz'
    tar = tarfile.open(filename)
    tar.extractall(filepath)
    tar.close()


def ls():
    filepath = dirname(abspath(__file__))
    filename = filepath + '/resources.tar.gz'
    tar = tarfile.open(filename)
    filelist = list(set(map(lambda x: x.split('/')[0], tar.getnames())))
    dirclist = os.listdir(filepath)
    datalist = list(filter(lambda x: x in filelist, dirclist)) 
    datalist.sort()

    print(datalist)


def load(pick):
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

