"""Statistical Hypothesis Tests.

"""


import warnings
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.stats.api as smt
import statsmodels.formula.api as smf


__all__ = ['f_test',
           'f_test_formula',
           'anova_test',
           'anova_test_formula',
           'chisq_test',
           'fisher_test']


def f_test(a, b, scale=1, alternative='two-sided',
           conf_level=.95, *args, **kwargs):
    """F-Test.

    """
    assert 0 < scale <= 1
    assert 0 < conf_level <= 1

    dfn = len(a) - 1
    dfd = len(b) - 1

    if (len(a) or len(b)) < 2:

        print('Observations are insufficient.')
        f_statistics = np.nan
        p_value = np.nan
        conf_min, conf_max = np.nan, np.nan

    else:

        try:
            f_statistics = np.array(a).var() / np.array(b).var()
        except ZeroDivisionError:
            f_statistics = np.nan

        p_value = st.f.cdf(np.abs(f_statistics), dfn, dfd, scale=scale)
        # p_value = distributions.t.sf(np.abs(t), df)

        conf_interval = st.f.interval(conf_level, dfn, dfd, scale=scale)
        conf_min, conf_max = np.multiply(f_statistics, conf_interval)

        if alternative == 'two-sided':
            p_value = 2 * np.min([p_value, 1-p_value])

        elif alternative == 'greater':
            p_value = st.f.sf(f_statistics, dfn, dfd, scale=scale)
            conf_min, conf_max = conf_min, np.inf

        elif alternative == 'less':
            conf_min, conf_max = 0, conf_max

    # print('F-Statistics: %.4g' % f_statistics)
    # print('dfn, dfd: %d %d' % (dfn, dfd) )
    # print('Hypothesized Scale: %d' % scale)
    # print('Confidence Level: %.3g' % conf_level)
    # print('Confidence Interval: %.4g, %.4g' % (conf_min, conf_max))
    # print('P-value: %.4g' % p_value)

    res = pd.Series({'f_statistics': f_statistics,
                     'dfn': dfn,
                     'dfd': dfd,
                     'hypo_scale': scale,
                     'conf_level': conf_level,
                     'conf_interval': (conf_min, conf_max),
                     'p_value': p_value})

    return res


def f_test_formula(a, b, scale=1, alternative='two-sided',
                   conf_level=.95, *args, **kwargs):
    """F-Test by formula.

    """
    assert 0 < scale <= 1
    assert 0 < conf_level <= 1

    dfn = len(a) - 1
    dfd = len(b) - 1

    if (len(a) or len(b)) < 2:

        print('Observations are insufficient.')
        f_statistics = np.nan
        p_value = np.nan
        conf_min, conf_max = np.nan, np.nan

    else:

        try:
            f_statistics = np.array(a).var() / np.array(b).var()
        except ZeroDivisionError:
            f_statistics = np.nan

        p_value = st.f.cdf(np.abs(f_statistics), dfn, dfd, scale=scale)
        # p_value = distributions.t.sf(np.abs(t), df)

        conf_interval = st.f.interval(conf_level, dfn, dfd, scale=scale)
        conf_min, conf_max = np.multiply(f_statistics, conf_interval)

        if alternative == 'two-sided':
            p_value = 2 * np.min([p_value, 1-p_value])

        elif alternative == 'greater':
            p_value = st.f.sf(f_statistics, dfn, dfd, scale=scale)
            conf_min, conf_max = conf_min, np.inf

        elif alternative == 'less':
            conf_min, conf_max = 0, conf_max


    # print('F-Statistics: %.4g' % f_statistics)
    # print('dfn, dfd: %d %d' % (dfn, dfd) )
    # print('Hypothesized Scale: %d' % scale)
    # print('Confidence Level: %.3g' % conf_level)
    # print('Confidence Interval: %.4g, %.4g' % (conf_min, conf_max))
    # print('P-value: %.4g' % p_value)

    res = pd.Series({'f_statistics': f_statistics,
                     'dfn': dfn,
                     'dfd': dfd,
                     'hypo_scale': scale,
                     'conf_level': conf_level,
                     'conf_interval': (conf_min, conf_max),
                     'p_value': p_value})

    return res


def anova_test(formula, data=None, typ=1):
    """ANOVA Test.

    """
    lin_model = smf.ols(formula, data=data).fit()
    res_anova = smt.anova_lm(lin_model, typ=typ)

    return res_anova, lin_model


def anova_test_formula(formula, data=None, typ=1):
    """ANOVA Test by formula.

    """
    lin_model = smf.ols(formula, data=data).fit()
    res_anova = smt.anova_lm(lin_model, typ=typ)

    return res_anova, lin_model


def chisq_test(data, x=None, y=None, correction=None,
               lambda_=None, margin=True, print_ok=True):
    """Chi-square Test.

    lambda_ gives the power in the Cressie-Read power divergence statistic.
    The default is 1.
    For convenience, lambda_ may be assigned one of the following strings,
    in which case the corresponding numerical value is used:

    String              Value   Description

    "pearson"             1     Pearson's chi-squared statistic.
                                In this case, the function is
                                equivalent to `stats.chisquare`.
    "log-likelihood"      0     Log-likelihood ratio. Also known as
                                the G-test [R623]_.
    "freeman-tukey"      -1/2   Freeman-Tukey statistic.
    "mod-log-likelihood" -1     Modified log-likelihood ratio.
    "neyman"             -2     Neyman's statistic.
    "cressie-read"        2/3   The power recommended in [R625]_.

    """
    dataChi = data[[x, y]].dropna()
    crossT = pd.crosstab(dataChi[x], dataChi[y], margins=margin)

    if margin:
        crossT_raw = crossT.iloc[:-1, :-1]
        (chiSqr,
         pValue,
         freeDeg,
         expectedV_raw) = st.chi2_contingency(crossT_raw,
                                              correction=correction,
                                              lambda_=lambda_)
        expectedV_raw = pd.DataFrame(expectedV_raw,
                                     index=crossT_raw.index,
                                     columns=crossT_raw.columns)

        expectedV = expectedV_raw.copy()
        expectedV['All'] = expectedV.sum(axis=1)
        expectedV = expectedV.append(expectedV.sum(axis=0).rename('All'))

    else:
        (chiSqr,
         pValue,
         freeDeg,
         expectedV_raw) = st.chi2_contingency(crossT,
                                              correction=correction,
                                              lambda_=lambda_)
        expectedV_raw = pd.DataFrame(expectedV_raw,
                                     index=crossT.index,
                                     columns=crossT.columns)

        expectedV = expectedV_raw

    check_chisq_rule = (expectedV_raw[expectedV_raw <= 5].count().sum() <=
                        (expectedV_raw.shape[0] * expectedV_raw.shape[1]) * .2)

    if print_ok:
        print('#'*20 + ' Chi-Square Test ' + '#'*20 + '\n')
        print('x : ' + x)
        print('y : ' + y)
        print('\n## Contingency Table')
        print('-'*50)
        print(crossT)
        print('-'*50)

        msg = """
## Chi-square Statistic : {}
## P-value : {}
## Degrees of Freedom : {}
"""

        print(msg.format(chiSqr, pValue, freeDeg))
        print('\n' + '## Expected Values')
        print('-'*60)
        print(expectedV)
        print('-'*60 + '\n')

    if not check_chisq_rule:
        w_msg1 = 'Warning: The precondition of Chi-Square was not implemented.'
        w_msg2 = 'Chi-squared approximation may be incorrect.'
        w_msg = '\n'.join([w_msg1, w_msg2])
        warnings.warn(w_msg)

    return pd.Series({'cross_t': crossT,
                      'chisq-stat': chiSqr,
                      'p_value': pValue,
                      'df': freeDeg,
                      'expected': expectedV})


def fisher_test(data, x=None, y=None, alternative='two-sided',
                margin=True, print_ok=True):
    """Fisher's Exact Test.

    """
    dataChi = data[[x, y]].dropna()
    crossT = pd.crosstab(dataChi[x], dataChi[y], margins=margin)

    if margin:
        crossT_raw = crossT.iloc[:-1, :-1]
        odds_ratio, p_value = st.fisher_exact(crossT_raw,
                                              alternative=alternative)
    else:
        odds_ratio, p_value = st.fisher_exact(crossT,
                                              alternative=alternative)

    if print_ok:
        print('#'*20 + ' Fisher\'s Exact Test ' + '#'*20 + '\n')
        print('x : ' + x)
        print('y : ' + y)
        print('\n## Contingency Table')
        print('-'*50)
        print(crossT)
        print('-'*50)

        msg = """
## Odds Ratio : {}
## P-value : {}
## Alternative Hypothesis : {}
"""

        print(msg.format(odds_ratio, p_value, alternative))
        print('-'*60 + '\n')

    return pd.Series({'odds_ratio': odds_ratio, 'p_value': p_value})


if __name__ == '__main__':

    a = [65,75,83,75,89,95,80,69,76,79,81,90,75,72,83,92,61,87,62.80]
    b = [54,65,91,76,79,78,84,97,88,75,72,68,76,85,72,88]

    # %%

    f_test(a, b)
    f_test(a, b, alternative='greater')
    f_test(a, b, alternative='less')
