#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 23:04:27 2017

@author: pydemia
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

__all__ = ['point_boxplot',
           'point_boxplot_grid']


def point_boxplot(value, by=None, data=None, dotcolor='b.', rot=90, spread=.2, dot_alpha=.2, *args, **kwargs):

    flierprops = dict(marker='o', markerfacecolor='white', alpha=1., markersize=5, linestyle='none', markeredgewidth=.7)

    plot = data.boxplot(value, by=by, rot=90, flierprops=flierprops, showfliers=True, showmeans=True, *args, **kwargs)

    pvt = pd.pivot_table(data, index=data.index, columns=by, values=value)

    for i in range(pvt.shape[1]):
        y = pvt[pvt.columns[i]]
        x = np.random.normal(i+1, spread/pvt.shape[1], len(y))
        plt.plot(x, y, dotcolor, alpha=dot_alpha)

    return plot


def point_boxplot_grid(value, grid_by=None, by=None, data=None, dotcolor='b.', rot=90, spread=.2, dot_alpha=.2, *args, **kwargs):

    
    flierprops = dict(marker='o', markerfacecolor='white', alpha=1., markersize=5, linestyle='none', markeredgewidth=.7)

    plot = data.boxplot(value, by=by, rot=90, flierprops=flierprops, showfliers=True, showmeans=True, *args, **kwargs)

    pvt = pd.pivot_table(data, index=data.index, columns=by, values=value)

    for i in range(pvt.shape[1]):
        y = pvt[pvt.columns[i]]
        x = np.random.normal(i+1, spread/pvt.shape[1], len(y))
        plt.plot(x, y, dotcolor, alpha=dot_alpha)

    return plot


