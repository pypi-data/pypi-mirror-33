"""Utility Objects.

This module provides a number of functions and objects for utility.

hypo_test
---------
- `f_test` -- F-Test.
- `f_test_formula` -- F-Test by formula.
- `anova_test` -- ANOVA Test.
- `anova_test_formula` -- ANOVA Test by formula.
- `chisq_test` -- Chi-square Test.
- `fisher_test` -- Fisher's Exact Test.

feature_selection
-----------------
- `lasso_rank` -- Feature selection by LASSO regression.
- `feature_selection_vif` -- VIF based stepwise feature selection
                             for multivariate analysis.

metrics
-------
- `deviation` -- Deviation.
- `vif` -- Variance inflation factor.
- `mean_absolute_percentage_error` -- Mean Absolute Percentage Error.
- `average_absolute_deviation` -- Average Absolute Deviation.
- `median_absolute_deviation` -- Median Absolute Deviation.
- `calculate_interaction` -- Feature interaction calculation.

formula
-------
- `from_formula` -- R-style Formula Formatting.

"""


from unipy.stats import metrics
from unipy.stats import hypo_test
from unipy.stats import feature_selection
from unipy.stats import formula


from unipy.stats.metrics import *
from unipy.stats.hypo_test import *
from unipy.stats.feature_selection import *
from unipy.stats.formula import *

__all__ = []
__all__ += metrics.__all__
__all__ += hypo_test.__all__
__all__ += feature_selection.__all__
__all__ += formula.__all__
