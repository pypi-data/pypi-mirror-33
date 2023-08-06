# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 20:55:26 2017

@author: Young Ju Kim
"""



if __name__ == '__main__':
    # Import dataset manager
    import unipy.dataset.api as dm

    # Extract Datasets for the first time
    dm.init()

    # Reset Datasets
    dm.reset()

    # Get a Dataset list
    dm.ls()

    # Load Datasets
    data = dm.load('anscombe')
    data = dm.load(2)
