#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import sys
sys.path.append('../')
from perfbench.process import *


def main():
    bm = Benchmark(
        datasets=[
            dict(stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64), title='float64')
        ],
        dataset_sizes=[2 ** n for n in range(3)],
        kernels=[
            dict(stmt=lambda x: np.around(x), label='around'),
            dict(stmt=lambda x: np.rint(x), label='rint')
        ],
        xlabel='dataset sizes',
        title='around vs rint'
    )
    bm.run()
    bm.plot()
    bm.save_as_html(filepath='plot1.html')
    bm.save_as_png(filepath='plot1.png')


if __name__ == '__main__':
    main()
