#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import sys
sys.path.append('../')
from perfbench.process import *


def main():
    setups = [
        {'func': lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64), 'title': 'float64'}
    ]

    kernels = [
        {'func': lambda x: np.around(x), 'label': 'around'},
        {'func': lambda x: np.rint(x), 'label': 'rint'}
    ]

    ntimes = [2 ** n for n in range(15)]

    bm = Benchmark(
        setups=setups,
        kernels=kernels,
        ntimes=ntimes,
        xlabel='samples',
        title='test',
        logx=True
    )

    bm.run()
    bm.show()


if __name__ == '__main__':
    main()
