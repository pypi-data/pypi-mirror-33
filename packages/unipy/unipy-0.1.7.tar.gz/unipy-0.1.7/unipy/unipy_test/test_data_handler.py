# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 20:55:26 2017

@author: Young Ju Kim

"""


if __name__ == '__main__':
    import numpy as np
    import unipy.dataset.api as dm
    from unipy.tools.data_handler import splitter, even_chunk
    from unipy.tools.data_handler import pair_unique, df_pair_unique
    from unipy.tools.data_handler import (merge_csv, nancumsum,
                                          timestamp_generator)
    from unipy.tools.data_handler import depth
    from unipy.tools.data_handler import zero_padder_2d, zero_padder_3d
    from unipy.tools.data_handler import ReusableGenerator, re_generator


    dm.init()

    # Function: splitter
    splitter(list(range(10)), how='equal', size=3)
    splitter(list(range(10)), how='remaining', size=3)

    # Function: even_chunk
    data = list(range(7))  # list, 1D
    chunked_gen = even_chunk(data, 3)
    next(chunked_gen)
    chunked = list(even_chunk(data, 3))

    data = np.arange(30).reshape(-1, 3)  # np.ndarray, 2D
    chunked_gen = even_chunk(data, 4)
    next(chunked_gen)

    # Function: pair_unique
    data = dm.load('titanic')
    pair_unique(data.iloc[:, 0], data.iloc[:, 1])

    # Function: df_pair_unique
    data = dm.load('titanic')
    df_pair_unique(data, ['Class', 'Sex'])
    df_pair_unique(data, ['Class', 'Sex'], to_frame=True)

    # Function: merge_csv
    data = dm.load('titanic')
    data.head(9)
    data.iloc[:2, :].to_csv('tmp1.csv', header=True, index=False)
    data.iloc[2:4, :].to_csv('tmp2.csv', header=True, index=False)
    data.iloc[4:9, :].to_csv('tmp3.csv', header=True, index=False)
    merged = merge_csv('./')
    print(merged)

    # Function: nancumsum
    tmp = [1, 2, 4]
    list(nancumsum(tmp))

    # Function: timestamp_generator
    begin, fin, period = 1, 10, 3
    list(timestamp_generator(begin, fin, period))
    time_sequence = timestamp_generator(begin, fin, period)
    time_msg = "{start:2} to {end:2}, {term:2} days."
    for time in time_sequence:
        b, f = time
        print(time_msg.format(start=b, end=f, term=period))

    # Function: depth
    tmp = [(1, 3), (4, 6), (7, 9), (10, 12)]
    depth(tmp)

    tmp3d = [[np.arange(i) + i for i in range(2, j)] for j in range(5, 10)]
    depth(tmp3d)

    tmp3d_dict = [{'key' + str(i): np.arange(i) + i for i in range(2, j)}
                  for j in range(5, 10)]
    depth(tmp3d_dict)

    # Function: zero_padder_2d
    tmp = [np.arange(i) + i for i in range(2, 5)]
    zero_padder_2d(tmp, max_len=5, method='forward')

    # Function: zero_padder_3d
    tmp3d = [np.arange(i * 2).reshape(-1, 2) for i in range(1, 5)]
    zero_padder_3d(tmp3d)

    # Class: ReusableGenerator
    gen = (i for i in range(10))
    regen = ReusableGenerator(gen)
    regen
    list(regen)
    list(regen)
    list(gen)
    list(regen)

    # Function: re_generator
    gen = (i for i in range(10))
    regen = re_generator(gen)
    regen
    list(regen)
    list(regen)
    list(gen)
    list(gen)
    list(gen)
    list(regen)
    list(regen)
