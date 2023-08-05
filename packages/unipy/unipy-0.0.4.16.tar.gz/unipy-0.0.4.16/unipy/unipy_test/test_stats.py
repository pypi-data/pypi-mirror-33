# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 20:55:26 2017

@author: Young Ju Kim
"""


#%% Sample datasets
import unipy.dataset.api as dm

# Extract Datasets for the first time
dm.init()

# Reset Datasets
dm.reset()

# Get a Dataset list
dm.ls()

# Load Datasets
wine1 = dm.load('winequality_red')
wine2 = dm.load('winequality_white')

#%% VIF
#from unipy.stats import feature_selection_vif as fsv

#res, drp = fsv(wine1, thresh=5.0)


#%% Inter-Action
#from unipy.stats import calculate_interaction
#rankedInter, regCoef, interActTbl = calculate_interaction(ranked, pvTbl, targetedCol, ranknum=10)
