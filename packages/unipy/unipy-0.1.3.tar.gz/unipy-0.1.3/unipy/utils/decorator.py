"""Docstring for ``decorator``.

========================
Function Decorator
========================
==================== =========================================================
Profiler
==============================================================================
time_profiler        Function running time command-line profiler.
time_logger          Function running time log profiler.
==================== =========================================================
==================== =========================================================
Commandline printout
==============================================================================
job_wrapper          Command-line line dragging tool.
==================== =========================================================
==================== =========================================================
Code Translation
==============================================================================
Infix                Function to operator translator.
infix                Functional API for ``Infix``.
==================== =========================================================
"""


import logging
from datetime import datetime as dt
from functools import partial
from functools import wraps


__all__ = ['time_profiler',
           'time_logger',
           'job_wrapper',
           'Infix',
           'infix']


def time_profiler(func):
    """Print wrapper for time profiling.

    This wrapper prints out start, end and elapsed time.

    Parameters
    ----------
    func: Function
        A function to profile.

    Returns
    -------
    Function
        A wrapped function.

    See Also
    --------
    ``functools.wraps``
    ``decorator``

    Examples
    --------
    >>> import unipy as up
    >>> @up.time_profiler
    ... def afunc(i):
    ...     return len(list(range(i)))
    ...
    >>> res = afunc(58)
    (afunc) Start   : 2018-06-20 22:11:35.511374
    (afunc) End     : 2018-06-20 22:11:35.511424
    (afunc) Elapsed :             0:00:00.000050
    >>> res
    58

    """
    @wraps(func)
    def profiler(*args, **kwargs):

        start_tm = dt.now()
        print("(%s) Start   : %26s" % (func.__name__, start_tm))

        res = func(*args, **kwargs)
        end_tm = dt.now()
        print("(%s) End     : %26s" % (func.__name__, end_tm))

        elapsed_tm = end_tm - start_tm
        print("(%s) Elapsed : %26s" % (func.__name__, elapsed_tm))
        return res

    return profiler


def time_logger(func):
    """Logging wrapper for time profiling.

    This wrapper logs start, end and elapsed time.

    Parameters
    ----------
    func: Function
        A function to profile.

    Returns
    -------
    Function
        A wrapped function.

    See Also
    --------
    ``functools.wraps``
    ``decorator``

    Examples
    --------
    >>> import unipy as up
    >>> @up.time_logger
    ... def afunc(i):
    ...     return len(list(range(i)))
    ...
    >>> res = afunc(58)
    (afunc) Start   : 2018-06-20 22:11:35.511374
    (afunc) End     : 2018-06-20 22:11:35.511424
    (afunc) Elapsed :             0:00:00.000050
    >>> res
    58

    """
    @wraps(func)
    def logger(*args, **kwargs):

        start_tm = dt.now()
        logging.info("(%s) Start   : %26s" % func.__name__ + str(start_tm))

        res = func(*args, **kwargs)

        end_tm = dt.now()
        logging.info("(%s) End     : %26s" % func.__name__ + str(end_tm))

        elapsed_tm = end_tm - start_tm
        logging.info("(%s) Elapsed : %26s" % func.__name__ + str(elapsed_tm))

        return res

    return logger


def job_wrapper(func):
    """Print wrapper for time profiling.

    This wrapper prints out start & end line.

    Parameters
    ----------
    func: Function
        A function to separate print-line job.

    Returns
    -------
    Function
        A wrapped function.

    See Also
    --------
    ``functools.wraps``
    ``decorator``

    Examples
    --------
    >>> import unipy as up
    >>> @up.job_wrapper
    ... def afunc(i):
    ...     return len(list(range(i)))
    ...
    >>> afunc(458)
    ----------- [afunc] START -----------

    -----------  [afunc] END  -----------

    afunc : 0:00:00.000023

    458

    """
    @wraps(func)
    def wrapper(*args, **kwargs):

        # Message Length = 40 + 2 (\n)
        dash_len = int((40 - len(func.__name__) - 12) / 2)

        start_msg = '-'*dash_len + ' [{}] START '.format(func.__name__) + \
                    '-'*dash_len + '\n'
        print(start_msg)
        start_tm = dt.now()

        res = func(*args, **kwargs)

        end_tm = dt.now()
        end_msg = '-'*dash_len + '  [{}] END  '.format(func.__name__) + \
                  '-'*dash_len + '\n'
        print(end_msg)
        print("{} :".format(func.__name__), end_tm - start_tm, '\n')

        return res

    return wrapper


class Infix(object):
    """Wrapper for define an operator.

    This wrapper translates a function to an operator.

    Returns
    -------
    Function
        A wrapped function.

    See Also
    --------
    ``functools.partial``
    ``decorator``

    Examples
    --------
    >>> @Infix
    ... def add(x, y):
    ...     return x + y
    ...
    >>> 5 |add| 6
    11
    >>> instanceof = Infix(isinstance)
    >>> 5 |instanceof| int
    True

    """
    def __init__(self, func):
        """__init__ method.

        Parameters
        ----------
        function: Function
            A function to translate as an operator.
        """
        self.func = func

    def __or__(self, other):
        return self.func(other)

    def __ror__(self, other):
        return Infix(partial(self.func, other))

    def __rshift__(self, other):
        return self.func(other)

    def __rlshift__(self, other):
        return Infix(partial(self.func, other))

    def __call__(self, lhs, rhs):
        return self.func(lhs, rhs)


def infix(func):
    """A functional API for Infix decorator.

    Returns
    -------
    Function
        A wrapped function.

    See Also
    --------
    ``unipy.utils.wrapper.infix``

    Examples
    --------
    >>> @infix
    ... def add(x, y):
    ...     return x + y
    ...
    >>> 5 |add| 6
    11
    >>> instanceof = infix(isinstance)
    >>> 5 |instanceof| int
    True

    """
    return Infix(func)
