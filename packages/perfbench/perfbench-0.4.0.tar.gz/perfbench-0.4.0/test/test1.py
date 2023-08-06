#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import sys
sys.path.append('../')
from perfbench.process import *


def main():
    bm = Benchmark(
        setups=[
            dict(func=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64), title='float64')
        ],
        kernels=[
            dict(func=lambda x: np.around(x), label='around'),
            dict(func=lambda x: np.rint(x), label='rint')
        ],
        ntimes=[2 ** n for n in range(15)],
        xlabel='samples',
        title='around vs rint',
        logx=True
    )
    bm.run()
    bm.plot()
    bm.save_as_html(filepath='plot1.html')
    bm.save_as_png(filepath='plot1.png')


if __name__ == '__main__':
    main()
