# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 01:04:13 2017

@author: Young Ju Kim
"""


__all__ = ['from_formula']


def from_formula(formula):

    yCol = formula.replace(' ', '').split('~')[0].strip()
    xCol = formula.replace(' ', '').split('~')[1].strip().split('+')
    
    return xCol, yCol
