"""Complexed Plotting Toolkit.

"""


import numpy as np
import pandas as pd
import collections
import matplotlib.pyplot as plt


__all__ = ['point_boxplot',
           'point_boxplot_axis']


def point_boxplot(data, groupby=None, value=None,
                  rot=90, spread=.2,
                  dot_size=15., dot_color='b', dot_alpha=.2,
                  *args, **kwargs):
    """Boxplot with points.

    Draw boxplots by given keys(groupby, value).

    Parameters
    ----------
    data: pandas.DataFrame
        a dataset.

    groupby: str or list-like (default: None)
        A key column to separate. (X-axis, categorical)
        When ``str``, it should be a column name to groupby.
        When ``list-like``, it contains a column name to groupby.

    value: str or list-like (default: None)
        A key column to get values. (Y-axis, numerical)
        When ``str``, it should be a column name of values.
        When ``list-like``, it contains a column name of values.

    rot: int (default: 90)
        A rotation angle to show X-axis labels.

    spread: float (default: .2)
        A spread ratio of points.
        The bigger, the pointing distribution width are broader.

    dot_size: float (default: 15.)
        A size of each points.

    dot_color: int (default: 'b')
        A color name of each points.

    dot_alpha: float (default: .2)
        A transparency value of each points.

    Returns
    -------
    matplotlib.figure.Figure
        A plot figure.

    Exceptions
    ----------
    AssertionError
        It is raised when two or more names are given to
        ``groupby`` or ``value``.

    See also
    --------
    ``pandas.DataFrame.boxplot``
    ``matplotlib.pyplot``

    Examples
    --------
    >>> import unipy.dataset.api as dm
    >>> from unipy.plots import point_boxplot
    >>> dm.init()
    >>> data = dm.load('iris')
    Dataset : iris
    >>> tmp = point_boxplot(data, groupby='species', value='sepal_length')

    """
    if isinstance(groupby, (list, tuple)):
        groupby_list = groupby
    elif isinstance(groupby, str):
        groupby_list = [groupby]

    if isinstance(value, (list, tuple)):
        value_list = value
    elif isinstance(value, str):
        value_list = [value]

    assert len(groupby_list) == 1, "'groupby': should be a single column"
    assert len(value_list) == 1, "'value': should be a single column"

    flierprops = dict(marker='o', markerfacecolor='white',
                      alpha=1., markersize=5,
                      linestyle='none', markeredgewidth=.7)

    grouped = data.groupby(groupby_list)[value_list]

    fig, ax = plt.subplots(nrows=1, ncols=1)

    data.boxplot(by=groupby_list, column=value_list, rot=rot, ax=ax,
                 flierprops=flierprops, showfliers=True,
                 showmeans=True)

    for i, (key, grp) in enumerate(grouped):
        axis_y_val = grp[value]
        axis_x_loc = np.random.normal(i + 1,
                                      spread / len(grouped),
                                      len(axis_y_val))
        ax.scatter(x=axis_x_loc, y=axis_y_val,
                   s=dot_size, c=dot_color, alpha=dot_alpha)

    fig.tight_layout()

    return fig


def point_boxplot_axis(data, groupby=None, value=None,
                       rot=90, spread=.2,
                       dot_size=15., dot_color='b', dot_alpha=.2,
                       share_yrange=True,
                       *args, **kwargs):
    """Boxplot with points, horizontally seperated.

    Draw boxplots by given keys(groupby, value).

    Parameters
    ----------
    data: pandas.DataFrame
        a dataset.

    groupby: str or list-like (default: None)
        A key column to separate. (X-axis, categorical)
        When ``str``, it should be a column name to groupby.
        When ``list-like``, it contains a column name to groupby.

    value: str or list-like (default: None)
        A key column to get values. (Y-axis, numerical)
        When ``str``, it should be a column name of values.
        When ``list-like``, it contains a column name of values.

    rot: int (default: 90)
        A rotation angle to show X-axis labels.

    spread: float (default: .2)
        A spread ratio of points.
        The bigger, the pointing distribution width are broader.

    dot_size: float (default: 15.)
        A size of each points.

    dot_color: int (default: 'b')
        A color name of each points.

    dot_alpha: float (default: .2)
        A transparency value of each points.

    share_yrange: Boolean (defalut: True)
        False then each Y-axis limit of boxplots will draw independent.

    Returns
    -------
    matplotlib.figure.Figure
        A plot figure.

    Exceptions
    ----------
    AssertionError
        It is raised when two or more names are given to
        ``groupby`` or ``value``.

    See also
    --------
    ``pandas.DataFrame.boxplot``
    ``matplotlib.pyplot``

    Examples
    --------
    >>> import unipy.dataset.api as dm
    >>> from unipy.plots import point_boxplot_axis
    >>> dm.init()
    >>> data = dm.load('iris')
    Dataset : iris
    >>> tmp = point_boxplot_axis(data,
    ...                          groupby='species',
    ...                          value='sepal_length',
    ...                          share_yrange=True)

    """
    if isinstance(groupby, (list, tuple)):
        groupby_list = groupby
    elif isinstance(groupby, str):
        groupby_list = [groupby]

    if isinstance(value, (list, tuple)):
        value_list = value
    elif isinstance(value, str):
        value_list = [value]

    assert len(groupby_list) == 1, "'groupby': should be a single column"
    assert len(value_list) == 1, "'value': should be a single column"

    flierprops = dict(marker='o', markerfacecolor='white',
                      alpha=1., markersize=5,
                      linestyle='none', markeredgewidth=.7)

    grouped = data.groupby(groupby_list)[value_list]
    ylim_min = data[value_list].min()[0]
    ylim_max = data[value_list].max()[0]

    fig, axes = plt.subplots(nrows=1, ncols=len(grouped))

    for ax, (i, (key, subdata)) in zip(axes.flatten(), enumerate(grouped)):
        subdata.boxplot(column=value_list, rot=rot, ax=ax,
                        flierprops=flierprops, showfliers=True,
                        showmeans=True)

        axis_y_val = subdata[value_list]
        axis_x_loc = np.random.normal(1,
                                      spread / len(grouped),
                                      len(axis_y_val))
        ax.scatter(x=axis_x_loc, y=axis_y_val,
                   s=dot_size, c=dot_color, alpha=dot_alpha)
        if share_yrange:
            ax.set_ylim(ylim_min, ylim_max)

    fig.tight_layout()

    return fig


def sector_plot():
    pass
