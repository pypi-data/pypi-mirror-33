# -*- coding: utf-8 -*-
"""
unipy
=====
Provides
  1. Data Handling Tools
  2. Statistical Functions.
  3. Function Wrappers to profile
  4. Generally-used Plots

How to use
----------
In terms of Data science, Data Preprocessing & Plotting is one of the most
annoying parts of Data Analysis. ``unipy`` offers you many functions maybe
once you have tried to search in ``google`` or ``stackoverflow``.

The docstring examples assume that `unipy` has been imported as `up`::
  >>> import numpy as up

Code snippets are indicated by three greater-than signs::
  >>> x = 42
  >>> x = x + 1

Use the built-in ``help`` function to view a function's docstring::
  >>> help(np.sort)
  ... # doctest: +SKIP

General-purpose documents like a glossary and help on the basic concepts
of numpy are available under the ``docs`` sub-module::
  >>> from numpy import docs
  >>> help(docs)
  ... # doctest: +SKIP

Available subpackages
---------------------
dataset
    Some famous datasets like ``iris``, ``titanic`` and ``adult``
image
    Image transformation tools.
math
    Mathmatical core functions for ``unipy`` itself
plots
    Most used plots
stats
    Statistic tools
tools
    Data handling tools
utils
    High-level wrappers & Python function decorators
unipy_test
    Test-codes of ``unipy``

"""


from unipy.__version__ import __version__

# from unipy import core
# from unipy import dataset
from unipy import math
from unipy import image
from unipy import plots
from unipy import stats
from unipy import tools
from unipy import utils

# from unipy.core import *
# from unipy.dataset import *
# from unipy.math import *
# from unipy.plots import *
# from unipy.image import *
# from unipy.stats import *
# from unipy.tools import *
# from unipy.utils import *

__all__ = []
__all__ += ['__version__']

# __all__ += core.__all__
__all__ += math.__all__
__all__ += plots.__all__
__all__ += image.__all__
__all__ += stats.__all__

# __all__ += dataset.__all__
__all__ += tools.__all__
__all__ += utils.__all__
