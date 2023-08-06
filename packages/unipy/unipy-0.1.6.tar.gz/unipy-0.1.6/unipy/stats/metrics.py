"""Metric Functions.

"""


import numpy as np
import pandas as pd
import statsmodels.api as sm
import itertools as it
import scipy.stats as st
from sklearn.preprocessing import PolynomialFeatures as pnf


__all__ = ['deviation',
           'vif',
           'mean_absolute_percentage_error',
           'average_absolute_deviation',
           'median_absolute_deviation',
           'calculate_interaction']


def deviation(container, method='mean', if_abs=True):

    """Deviation.

    """
    if method == 'mean':
        center = np.nanmean(container)
    elif method == 'median':
        center = np.nanmedian(container)

    resIter = map(lambda x: x - center, container)

    if if_abs:
        resIter = map(np.absolute, resIter)

    res = np.fromiter(resIter, dtype=np.float)

    return res


def vif(y, X):
    """Variance inflation factor.

    """
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


def calculate_interaction(rankTbl, pvTbl, target, ranknum=10):
    """Feature interaction calculation.

    """
    rankTop = rankTbl[:ranknum]
    interPvt = pvTbl[rankTop['var_name']]
    interAct = pnf(degree=2, interaction_only=True)

    interTbl = pd.DataFrame(interAct.fit_transform(interPvt),
                            index=interPvt.index).iloc[:, 1:]
    rankTop_col = list(rankTop['var_name'])
    interAct_col = list(map(' xx '.join,
                        list(it.combinations(rankTop['var_name'], 2))))
    interTbl.columns = rankTop_col + interAct_col

    # Generate a Result Table
    col = ['slope', 'intercept', 'corr_coef', 'p_value', 'std_err']
    ind = interTbl.columns
    regMatrix = pd.DataFrame(index=ind, columns=col)

    # Regression
    Y = pvTbl[target]
    for _ in range(interTbl.shape[1]):
        x = interTbl.ix[:, _]
        regMatrix.iloc[_, ] = st.linregress(x, Y)

    regMatrix['abs_corr_coef'] = abs(regMatrix['corr_coef'])
    regMatrix.sort_values(by='p_value', ascending=True, inplace=True)

    rank = regMatrix[(regMatrix['p_value'] < .01) &
                     (regMatrix['abs_corr_coef'] >= .3)]

    rank = rank.reset_index()
    rank['inter_name'] = rank['index']
    rank = rank[rank['inter_name'].str.find(' xx ') != -1]
    rank['rank'] = range(1, len(rank) + 1)

    rankCol = ['rank', 'inter_name', 'p_value',
               'corr_coef', 'abs_corr_coef',
               'std_err', 'slope', 'intercept']
    rank = rank[rankCol]

    return rank, regMatrix, interTbl
