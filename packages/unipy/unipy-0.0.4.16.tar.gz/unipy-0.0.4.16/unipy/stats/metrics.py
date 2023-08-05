# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 03:46:03 2017

@author: Young Ju Kim
"""


import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm

__all__ = ['deviation',
           'vif',
           'mean_absolute_percentage_error',
           'average_absolute_deviation',
           'median_absolute_deviation',
           'feature_selection_vif']


def deviation(container, method='mean', if_abs=True):

    if method == 'mean':
        center = np.nanmean(container)
    elif method == 'median':
        center = np.nanmedian(container)

    resIter = map(lambda x: x - center, container)

    if if_abs == True:
        resIter = map(np.absolute, resIter)

    res = np.fromiter(resIter, dtype=np.float)

    return res



def vif(y, X):

    assert isinstance(y, pd.Series)
    assert isinstance(X, pd.DataFrame)

    # Change input to array
    y_arr = y.values
    X_arr = X.values

    # Calculate a linear regression(Ordinary Least Square)
    reg = sm.add_constant(X_arr)
    est = sm.OLS(y_arr, reg).fit()

    # Get a R-square
    rsq = est.rsquared

    # Get a VIF
    vif = 1 / (1 - rsq)

    return vif


def mean_absolute_percentage_error(measure, predict, thresh=3.0):
    '''Mean Absolute Percentage Error.
    It is a percent of errors.
    It measures the prediction accuracy of a forecasting method in Statistics
    with the real mesured values and the predicted values, for example in trend
    estimation.
    If MAPE is 5, it means this prediction method potentially has 5% error.
    It cannot be used if there are zero values,
    because there would be a division by zero.
    '''
    mape = np.mean(np.absolute((measure - predict) / measure)) * 100

    return mape


def average_absolute_deviation(measure, predict, thresh=2):
    '''Average Absolute Deviation.
    It is ...
    It measures the prediction accuracy of a forecasting method in Statistics
    with the real mesured values and the predicted values, for example in trend
    estimation.
    If MAD is 5, it means this prediction method potentially has...
    '''
    aad = np.mean(np.absolute(measure - predict))

    return aad


def median_absolute_deviation(measure, predict, thresh=2):
    '''Median Absolute Deviation.
    It is ...
    It measures the prediction accuracy of a forecasting method in Statistics
    with the real mesured values and the predicted values, for example in trend
    estimation.
    If MAD is 5, it means this prediction method potentially has...
    '''
    mad = np.median(np.absolute(measure - predict))

    return mad


def feature_selection_vif(data, thresh=5.0):
    '''Stepwise Feature Selection for multivariate analysis.

    It calculates OLS regressions and the variance inflation factors iterating
    all explanatory variables. If the maximum VIF of a variable is over the
    given threshold, It will be dropped. This process is repeated until all
    VIFs are lower than the given threshold.

    Recommended threshold is lower than 5, because if VIF is greater than 5,
    then the explanatory variable selected is highly collinear with the other
    explanatory variables, and the parameter estimates will have large standard
    errors because of this.

    Parameters
    ----------
    data : DataFrame, (rows: observed values, columns: multivariate variables)
        design dataframe with all explanatory variables, as for example used in
        regression

    thresh : int, float
        A threshold of VIF

    Returns
    -------
    Filtered_data : DataFrame
        A subset of the input DataFame

    dropped_List : DataFrame
        'var' column : dropped variable names from input data columns
        'vif' column : variance inflation factor of dropped variables

    Notes
    -----
    This function does not save the auxiliary regression.

    See Also
    --------
    statsmodels.stats.outliers_influence.variance_inflation_factor

    References
    ----------
    http://en.wikipedia.org/wiki/Variance_inflation_factor

    '''
    assert isinstance(data, pd.DataFrame)

    # Create Dropped variable list
    dropped = pd.DataFrame(columns=['var', 'vif'])

    # Startswith 'drop = True'(Assume that some variables will be dropped)
    dropCondition = True

    # Calculate a VIF & Drop columns(variables)
    while dropCondition:

        # 1. Calculate a VIF
        vifDict = {col: vif(data.loc[:, col], data.loc[:, data.columns != col])
                   for col in data.columns}

        # Get the MAXIMUM VIF
        maxVar = max(vifDict, key=vifDict.get)
        maxVal = vifDict[maxVar]

        # 2. IF VIF values are over the threshold, THEN drop it
        if maxVal >= thresh:

            # Keep it
            dropped = dropped.append({'var': maxVar, 'vif': maxVal},
                                     ignore_index=True)

            # Drop it
            data = data.drop(maxVar, axis=1)

            # Print it
            print("Dropping '" + str(maxVar) + "' " + " VIF: " + str(maxVal))

            # Since a variable has been dropped, the assumption remains
            dropCondition = True

        else:

            # No variable dropped, the assumption has been rejected
            dropCondition = False

    # Print Massages
    remainsMsg = '# Remaining Variables '
    msgWrapper = '-' * (len(remainsMsg)+1)

    print('\n' + msgWrapper + '\n' + remainsMsg + '\n' + msgWrapper)
    print(list(data.columns))
    print('\n')

    droppedMsg = '# Dropped Variables '
    msgWrapper = '-' * (len(remainsMsg)+1)
    print('\n' + msgWrapper + '\n' + droppedMsg + '\n' + msgWrapper)
    print(list(dropped.loc[:, 'var']))
    print('\n')

    return data, dropped



