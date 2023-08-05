#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 17:05:27 2017

@author: dawkiny
"""

import itertools as it
import datetime as dt
import multiprocessing as mpr

__all__ = ['split_generator',
           'exceptor',
           'multiprocessor',
           'num_fromto_generator',
           'dt_fromto_generator',
           'tm_fromto_generator',
           'uprint']


def split_generator(iterable, size):

    data = iter(iterable)
    item = list(it.islice(data, size))

    while item:
        yield item
        item = list(it.islice(data, size))


def exceptor(x, exceptlist):
    
    res = [member for member in x if member not in exceptlist]
    
    return res
   


def multiprocessor(func, processes=2, arg_zip=None, *args, **kwargs):

    pool = mpr.pool.Pool(processes=processes)
    resp = pool.starmap(func, arg_zip, *args, **kwargs)

    return resp


def num_fromto_generator(start, end, term):
    pre, nxt = start, start + term -1
    yield pre, nxt
    while nxt < end:
        pre, nxt = nxt, nxt + term
        yield pre+1, nxt


def dt_fromto_generator(start, end, day_term, tm_format='%Y%m%d'):
    
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


def uprint(*args, print_ok=True, **kwargs):
    if print_ok:
        print(*args, **kwargs)
    

if __name__ == '__main__':
    res = [item for item in tm_fromto_generator(10001, 300000, 100000)]
    
    queryStr = """
SELECT *
FROM employees.employees
WHERE EMP_NO BETWEEN {pre} AND {nxt}
;
"""

    qList = [queryStr.format(pre=item[0], nxt=item[1]) \
             for item in num_fromto_generator(10001, 300000, 100000)]
    
    dtList = [item for item in dt_fromto_generator('20170101','20170331', 10)]
    tmList = [item for item in tm_fromto_generator('20170101','20170331', 10)]
    
    
    # multiprocessor
    def a_job(num, start, end):
        
        print('%d JobStart' % num)
        res = []
        for i in range(start, end+1):
            res.append(i)
        print('%d JobEnd' % num)
        return res

    a = list(range(1, 20))
    b = list(range(1, 20))
    c = list(range(1000000, 1000020))
    res = up.multiprocessor(a_job, processes=5, arg_zip=zip(a, b, c))
    
###
# list(filter(lambda col: col not in ['capital_gain'], test.columns))
# [member for member in test.columns if member not in ['capital_gain']]
