# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 03:46:03 2017

@author: Young Ju Kim
"""


#import numba as nb
import numpy as np
import pandas as pd
import sklearn as skl
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso
from unipy.stats.formula import from_formula


__all__ = ['lasso_rank']


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


if __name__ == '__main__':

    import unipy.dataset.api as dm
    dm.init()
    wine_red = dm.load('winequality_red')

    ranked, best_by_intercept, coefTbl, kBest, kBestPred = lasso_rank(X=wine_red.columns.drop('quality'), y=['quality'], data=wine_red)



