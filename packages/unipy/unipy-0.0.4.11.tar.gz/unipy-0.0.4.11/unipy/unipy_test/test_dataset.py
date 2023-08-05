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

