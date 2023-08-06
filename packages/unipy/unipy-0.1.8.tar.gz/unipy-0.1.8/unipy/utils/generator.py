"""Docstring for ``generator``.

========================
Versatile Generators
========================
==================== =========================================================
Productivity
==============================================================================
ReusableGenerator    Reusable Generator.
re_generator         Functional API for ``ReusableGenerator``.
==================== =========================================================
==================== =========================================================
Lazy Evaluation
==============================================================================
split_generator      Split data by given size.
==================== =========================================================
==================== =========================================================
Range Generator
==============================================================================
num_fromto_generator Range number string pairs by given term.
dt_fromto_generator  Range date format string pairs by given term.
tm_fromto_generator  Range datetime format string pairs by given term.
timestamp_generator  Range timestamp string pairs by given term.
==================== =========================================================
"""


import itertools as it
import datetime as dt


__all__ = ['ReusableGenerator',
           're_generator',
           'split_generator',
           'num_fromto_generator',
           'dt_fromto_generator',
           'tm_fromto_generator',
           'timestamp_generator']


class ReusableGenerator(object):
    """Temporary Interface to re-use generator for convenience.

    Once assigned, It can be infinitely consumed
    **as long as an input generator remains un-exhausted.

    Attributes
    ----------
    _source: generator
        A source generator.

    See Also
    --------
    generator
    ``itertools.tee``

    Examples
    --------
    >>> from unipy.utils.generator import ReusableGenerator
    >>> gen = (i for i in range(10))
    >>> gen
    <generator object <genexpr> at 0x11120ebf8>
    >>> regen = ReusableGenerator(gen)
    >>> regen
    <unipy.utils.generator.ReusableGenerator object at 0x1061a97f0>
    >>> list(regen)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(regen)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(gen)  # If the source is used, copied one will be exhausted too.
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(gen)
    []
    >>> list(regen)
    []

    """
    def __init__(self, generator):
        """__init__ method.

        Parameters
        ----------
        generator: generator
            An generator to copy.
            This original generator should not be used anywhere else.

        """
        self._copy(generator)

    def __iter__(self):
        """__iter__ method.

        """
        self._copy(self._dummy)
        return self._source.__iter__()

    def __next__(self):
        """__next__ method.

        """
        if self._source is None:
            self._copy(self._dummy)
        try:
            return self._source.__next__()
        except StopIteration:
            self._source = None
            raise

    def _copy(self, generator):
        """A private method for copy the given generator.

        """
        self._source, self._dummy = it.tee(generator)


def re_generator(generator):
    """A functional API for unipy.ReusableGenerator.

    Once assigned, It can be infinitely consumed
    **as long as an output generator is called at least one time.

    Parameters
    ----------
    generator: generator
        An generator to copy.
        This original generator should not be used anywhere else,
        until the copied one consumed at least once.

    Returns
    -------
    generator
        A generator to be used infinitely.

    See Also
    --------
    generator
    ``itertools.tee``

    Examples
    --------
    >>> from unipy.utils.generator import re_generator
    >>> gen = (i for i in range(10))
    >>> gen
    <generator object <genexpr> at 0x11120ebf8>
    >>> regen = copy_generator(gen)
    >>> regen
    <unipy.utils.generator.ReusableGenerator object at 0x1061a97f0>
    >>> list(regen)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(regen)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(gen)  # Once the copied one is used, the source will be exhausted.
    []
    >>> list(gen)
    []
    >>> list(regen)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(regen)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    """
    return ReusableGenerator(generator)


def split_generator(iterable, size):

    data = iter(iterable)
    item = list(it.islice(data, size))

    while item:
        yield item
        item = list(it.islice(data, size))


def num_fromto_generator(start, end, term):
    """A range function yields pair chunks.

    It had made for time-formatting query.
    It yields a tuple of (start, start+(term-1)) pair, until start > end.

    Parameters
    ----------
    *args: int
        end or start, end[, term]
        It works like range function.

    Yields
    -------
    tuple
        A tuple of (start, start+(term-1)) pair, until start > end.

    See Also
    --------
    ``yield``

    Examples
    --------
    >>> from unipy.utils.generator import num_fromto_generator
    >>>
    >>> query = 'BETWEEN {pre} AND {nxt};'
    >>>
    >>> q_list = [query.format(pre=item[0], nxt=item[1])
    ...           for item in num_fromto_generator(1, 100, 10)]
    >>> print(q_list[0])
    BETWEEN 1 AND 10;
    >>> print(q_list[1])
    BETWEEN 11 AND 20;

    """
    pre, nxt = start, start + term - 1
    yield pre, nxt
    while nxt < end:
        pre, nxt = nxt, nxt + term
        yield pre + 1, nxt


def dt_fromto_generator(start, end, day_term, tm_format='%Y%m%d'):
    """A range function yields datetime formats by pair.

    It had made for time-formatting query.
    It yields a tuple of (start, start+(term-1)) pair, until start > end.

    Parameters
    ----------
    start: str
        start datetime like 'yyyymmdd'.

    end: str
        start datetime like 'yyyymmdd'.

    day_term: int
        term of days.

    tm_format: (default: '%Y%m%d')
        datetime format string.

    Yields
    -------
    tuple
        A tuple of (start, start+(term-1)) pair, until start > end.

    See Also
    --------
    ``yield``

    Examples
    --------
    >>> from unipy.utils.generator import dt_fromto_generator
    >>> dt_list = [item for item in
    ...            dt_fromto_generator('20170101','20170331', 10)]
    >>> dt_list[:3]
    [('20170101', '20170110'),
     ('20170111', '20170120'),
     ('20170121', '20170130')]

    """
    pre = dt.datetime.strptime(start, tm_format)
    term = dt.timedelta(days=day_term)
    nxt = pre + dt.timedelta(days=day_term-1)
    end = dt.datetime.strptime(end, tm_format)

    yield pre.strftime(tm_format), nxt.strftime(tm_format)

    while nxt < end:
        pre, nxt = nxt, nxt + term

        res_pre, res_nxt = pre + dt.timedelta(days=1), nxt
        yield res_pre.strftime(tm_format), res_nxt.strftime(tm_format)


def tm_fromto_generator(start, end, day_term,
                        tm_string=['000000', '235959'], tm_format='%Y%m%d'):
    """A range function yields datetime formats by pair.

    It had made for time-formatting query.
    It yields a tuple of (start, start+(term-1)) pair, until start > end.

    Parameters
    ----------
    start: str
        start datetime like 'yyyymmdd'.

    end: str
        start datetime like 'yyyymmdd'.

    day_term: int
        term of days.

    tm_string: list (default: ``['000000', '235959']``)
        time strings to concatenate.

    tm_format: (default: '%Y%m%d')
        datetime format string.

    Yields
    -------
    tuple
        A tuple of (start, start+(term-1)) pair, until start > end.

    See Also
    --------
    ``yield``

    Examples
    --------
    >>> from unipy.utils.generator import tm_fromto_generator
    >>> tm_list = [item for item in
    ...            tm_fromto_generator('20170101','20170331', 10)]
    >>> tm_list[:3]
    [('20170101000000', '20170110235959'),
     ('20170111000000', '20170120235959'),
     ('20170121000000', '20170130235959')]

    """
    pre = dt.datetime.strptime(start, tm_format)
    term = dt.timedelta(days=day_term)
    nxt = pre + dt.timedelta(days=day_term-1)
    end = dt.datetime.strptime(end, tm_format)

    yield (pre.strftime(tm_format) + tm_string[0],
           nxt.strftime(tm_format) + tm_string[1])

    while nxt < end:
        pre, nxt = nxt, nxt + term

        res_pre, res_nxt = pre + dt.timedelta(days=1), nxt
        yield (res_pre.strftime(tm_format) + tm_string[0],
               res_nxt.strftime(tm_format) + tm_string[1])


def timestamp_generator(*args):
    """A range function yields pair timestep strings.

    It had made for time-formatting query.
    It yields a tuple of (start, start+(term-1)) pair, until start > end.

    Parameters
    ----------
    *args: int
        end or start, end[, term]
        It works like range function.

    Yields
    -------
    tuple
        A tuple of (start, start+(term-1)) pair, until start > end.

    See Also
    --------
    ``yield``

    Examples
    --------
    >>> from unipy.utils.generator import timestamp_generator
    >>> timestamp_generator(1, 10, 2)
    <generator object timestamp_generator at 0x10f519678>
    >>> list(timestamp_generator(1, 14, 5))
    [(1, 5), (6, 10), (11, 15)]
    >>> begin, fin, period = 1, 10, 3
    >>> list(timestamp_generator(begin, fin, period))
    [(1, 3), (4, 6), (7, 9), (10, 12)]
    >>> time_sequence = timestamp_generator(begin, fin, period)
    >>> time_msg = "{start:2} to {end:2}, {term:2} days."
    >>> for time in time_sequence:
    ... b, f = time
    ... print(time_msg.format(start=b, end=f, term=period))
    ...
     1 to  3,  3 days.
     4 to  6,  3 days.
     7 to  9,  3 days.
    10 to 12,  3 days.

    """
    args_tuple = (*args, )
    args_len = len(args_tuple)
    if args_len == 1:
        start, (end, ), term = 0, args_tuple, 2
    elif args_len == 2:
        (start, end), term = args_tuple, 2
    elif args_len == 3:
        start, end, term = args_tuple
    elif args_len > 4:
        raise TypeError('expected at most 3 arguments, got %s' % args_len)

    pre, nxt = start, start + term - 1
    yield pre, nxt
    while nxt < end:
        pre, nxt = nxt, nxt + term
        yield pre + 1, nxt
