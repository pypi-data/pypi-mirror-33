#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 23:43:37 2017

@author: pydemia
"""


import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels
import statsmodels.api as sm
import sklearn as skl
import unipy
import unipy.dataset.api as dm

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sbn


dm.init()
data01 = dm.load('iris')
data02 = data01.iloc[:, :2]

col01 = data01['sepal_length']
col02 = data01['sepal_width']
col03 = data01['petal_length']
col04 = data01['petal_width']


data11 = dm.load('adult')
data11.columns
data11

col11 = data11['education']
col12 = data11['race']


#data11 = dm.load('titanic')
#data11.columns
#data11
#dm.ls()
#col11 = data11['Class']
#col12 = data11['Survived']

# %% T-test

import sklearn as skl

# 1 sample
t_stat, pvalue = st.ttest_1samp(col01, col01.mean(), axis=0, nan_policy='propagate')

# 2 independents have identical averages. 
# (This test assumes that the populations have identical variances.)
st.ttest_ind(col01, col02, axis=0, equal_var=True)
sm.stats.ttest_ind(col01, col02)

#plt.hist(col01, bins=None)
#plt.hist(col02, bins=None)
#col01.plot(kind='density')
#data02.plot(kind='density')
#sbn.distplot(col01)
#sbn.kdeplot(col01)

# check 2 related or repeated samples have identical averages.
# Defines how to handle when input contains nan.
# ‘propagate’ returns nan
# ‘raise’ throws an error
# ‘omit’ performs the calculations ignoring nan values
st.ttest_rel(col01, col02, axis=0, nan_policy='propagate')

#data02.plot(kind='density')


# %% KS-Test
# Kolmogorov-Smirnov test for goodness of fit
st.kstest('norm', False, N=20, alternative='two-sided', mode='approx')


# %% Chi-Square Test
# One-way X2 test

st.chisquare(col01, col02)
st.chi2_contingency(col01, col02)
#st.chi2_contingency(col11, col12)

unipy.chisq_test(data11, x='education', y='race')

# %% Bartlett Test
# Test for equal variances

st.bartlett(col01, col02)

# %% Levene Test

st.levene(col01, col02, center='median')

# %% One-way ANOVA

st.f_oneway(col01, col02, col03)

# %% Lasso


#unipy.lasso(data01.iloc[:, :-1])

