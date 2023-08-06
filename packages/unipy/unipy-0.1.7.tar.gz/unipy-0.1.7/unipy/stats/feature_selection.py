"""Feature selection.

"""


# import numba as nb
import numpy as np
import pandas as pd
import sklearn as skl
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso
from unipy.stats.formula import from_formula


__all__ = ['lasso_rank',
           'feature_selection_vif']


# Defining a Lasso generic function
def _lasso_for_loop(data, X=None, y=None, alpha=.0001, *args, **kwargs):

    # Fit to the model
    lassoReg = Lasso(alpha=alpha, fit_intercept=True,
                     normalize=True, precompute=False,
                     max_iter=1e5, tol=1e-7,
                     warm_start=False, positive=False,
                     selection='cyclic', *args, **kwargs)

    lassoReg.fit(data[X], data[y].squeeze())
    yPredict = lassoReg.predict(data[X])

    # Return the result in pre-defined format
    rss = np.sum((yPredict - data[y].squeeze()) ** 2)
    ret = [rss]
    ret.extend([lassoReg.intercept_])
    ret.extend(lassoReg.coef_)

    return ret, yPredict


def lasso_rank(formula=None, X=None, y=None, data=None,
               alpha=np.arange(1e-5, 1e-2, 1e-4), k=2, plot=False,
               *args, **kwargs):
    """Feature selection by LASSO regression.

    Parameters
    ----------
    formula:
        R-style formula string

    X: list-like
        Column values for X.

    y: list-like
        A column value for y.

    data: pandas.DataFrame
        A DataFrame.

    alpha: Iterable
        An Iterable contains alpha values.
    k: int
        Threshold of coefficient matrix

    plot: Boolean (default: False)
        True if want to plot the result.

    Returns
    -------
    rankTbl: pandas.DataFrame
        Feature ranking by given ``k``.

    minIntercept: pandas.DataFrame
        The minimum intercept row in coefficient matrix.

    coefMatrix: pandas.DataFrame
        A coefficient matrix.

    kBest: pandas.DataFrame
        When Given ``k``, The best intercept row in coefficient matrix.

    kBestPredY: dict
        A predicted ``Y`` with ``kBest`` alpha.

    Example
    -------
    >>> import unipy.dataset.api as dm
    >>> dm.init()
    ['cars', 'anscombe', 'iris', 'nutrients', 'german_credit_scoring_fars2008', 'winequality_red', 'winequality_white', 'titanic', 'car90', 'diabetes', 'adult', 'tips', 'births_big', 'breast_cancer', 'air_quality', 'births_small']
    >>> wine_red = dm.load('winequality_red')
    Dataset : winequality_red
    >>>
    >>> ranked, best_by_intercept, coefTbl, kBest, kBestPred = lasso_rank(X=wine_red.columns.drop('quality'), y=['quality'], data=wine_red)
    >>> ranked
                      rank  lasso_coef  abs_coef
    volatile_acidity     1   -0.675725  0.675725
    alcohol              2    0.194865  0.194865
    >>> best_by_intercept
                          RSS  Intercept  fixed_acidity  volatile_acidity  \
    alpha_0.00121  691.956364   3.134874       0.002374         -1.023793

                   citric_acid  residual_sugar  chlorides  free_sulfur_dioxide  \
    alpha_0.00121          0.0             0.0  -0.272912                 -0.0

                   total_sulfur_dioxide  density   pH  sulphates   alcohol  \
    alpha_0.00121             -0.000963     -0.0 -0.0   0.505956  0.264552

                   var_count
    alpha_0.00121          6
    >>>
    """
    if formula is not None:
        X, y = from_formula(formula)
    else:
        X = list(X)
        y = y

    # Iterate over the alpha values
    coefMatrix = {'alpha_%.5f' % a: _lasso_for_loop(data, X=X, y=y, alpha=a, *args, **kwargs)[0] for a in alpha}
    predict    = {'alpha_%.5f' % a: _lasso_for_loop(data, X=X, y=y, alpha=a, *args, **kwargs)[1] for a in alpha}

    coefMatrix = pd.DataFrame(coefMatrix).T
    coefMatrix.columns = ['RSS', 'Intercept'] + X
    coefMatrix['var_count'] = coefMatrix.apply(np.count_nonzero, axis=1) - 2

    # Filter by thresh >= var_count
    kBest = coefMatrix[coefMatrix['var_count'] <= k]
    kBest = kBest.loc[kBest[['var_count']].idxmax()]
    kBest = kBest.loc[kBest[['Intercept']].idxmin()]

    # Minumum Intercept
    minIntercept = coefMatrix.loc[coefMatrix[['Intercept']].idxmin()]

    # Get Predicted Y value
    alphaVal = kBest.index[0]
    kBestPredY = {alphaVal: predict[alphaVal]}

    # Get a Rank Table
    lassoVal = kBest.iloc[:, kBest.squeeze().nonzero()[0].tolist()[2:-1]]
    filteredTbl = pd.concat([lassoVal.T, abs(lassoVal).T], axis=1)
    filteredTbl.columns = ['lasso_coef', 'abs_coef']
    filteredTbl = filteredTbl.sort_values(by='abs_coef', ascending=False)
    filteredTbl['rank'] = range(1, len(filteredTbl) + 1)
    rankTbl = filteredTbl[['rank', 'lasso_coef', 'abs_coef']]

    # Plots
    #fig = plt.figure(figsize=(12, 9))
    #title = 'Top {} variables : absolute coefficient by Lasso'.format(len(filteredTbl))
    #rankTbl['abs_coef'].plot(kind='barh')
    #fig.suptitle(title, fontsize=14, fontweight='bold')
    #plt.tight_layout(pad=5)

    return rankTbl, minIntercept, coefMatrix, kBest, kBestPredY


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
