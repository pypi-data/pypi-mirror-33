"""Docstring for ``wrapper``.

========================
High-level Code Wrapper
========================
==================== =========================================================
Operation Wrapper
==============================================================================
multiprocessor       Functional wrapper for multiprocessing.
==================== =========================================================
==================== =========================================================
Interfaces
==============================================================================
uprint               Print option interface within a function.
==================== =========================================================
"""


import multiprocessing as mpr


__all__ = ['multiprocessor',
           'uprint']


def multiprocessor(func, worker=2, arg_zip=None, *args, **kwargs):
    """Use multiprocessing as a function.

    Just for convenience.

    Parameters
    ----------
    func: Function
      Any function without ``lambda``.

    worker: int (default: 2)
      A number of processes.

    arg_zip: zip (default: None)
      A ``zip`` instance.

    Returns
    -------
    list
      A list contains results of each processes.

    See Also
    --------
    ``multiprocessing.pool``

    Examples
    --------
    >>> from unipy.utils.wrapper import multiprocessor
    >>> alist = [1, 2, 3]
    >>> blist = [-1, -2, -3]
    >>> def afunc(x, y):
    ...     return x + y
    ...
    >>> multiprocessor(afunc, arg_zip=zip(alist, blist))
    [0, 0, 0]
    >>> def bfunc(x):
    ...     return x + 2
    ...
    >>> multiprocessor(bfunc, arg_zip=zip(alist))
    [3, 4, 5]

    """
    with mpr.pool.Pool(processes=worker) as pool:
        resp = pool.starmap(func, arg_zip, *args, **kwargs)

    return resp


def uprint(*args, print_ok=True, **kwargs):
    """Print option interface.

    This function is equal to ``print`` function but added ``print_ok``
    option. This allows you to control printing in a function.

    Parameters
    ----------
    *args: whatever ``print`` allows.
      It is same as ``print`` does.

    print_ok: Boolean (default: True)
      An option whether you want to print something out or not.

    arg_zip: zip (default: None)
      A ``zip`` instance.

    """
    if print_ok:
        print(*args, **kwargs)
