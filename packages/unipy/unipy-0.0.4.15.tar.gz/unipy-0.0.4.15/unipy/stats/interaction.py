import numpy as np
import pandas as pd
import itertools as it
import scipy.stats as st
from sklearn.preprocessing import PolynomialFeatures as pnf

__all__ = ['calculate_interaction']

def calculate_interaction(rankTbl, pvTbl, target, ranknum=10):
    
    rankTop = rankTbl[:ranknum]
    interPvt = pvTbl[rankTop['var_name']]
    interAct = pnf(degree=2, interaction_only=True)
    
    interTbl = pd.DataFrame(interAct.fit_transform(interPvt), index=interPvt.index).iloc[:, 1:]
    interTbl.columns = list(rankTop['var_name']) + list(map(' xx '.join, list(it.combinations(rankTop['var_name'], 2))))
    
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
    

if __name__ == '__main__':
    #rankedInter, regCoef, interActTbl = calculate_interaction(ranked, pvTbl, targetedCol, ranknum=10)
    pass
