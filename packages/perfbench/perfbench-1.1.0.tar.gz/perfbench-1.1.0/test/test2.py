#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import sys
sys.path.append('../')
from perfbench.process import *


def main():
    bm = Benchmark(
        datasets=[
            dict(stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float16), title='float16'),
            dict(stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float32), title='float32'),
            dict(stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64), title='float64')
        ],
        dataset_sizes=[2 ** n for n in range(3)],
        kernels=[
            dict(stmt=lambda x: np.around(x), label='around'),
            dict(stmt=lambda x: np.rint(x), label='rint'),
        ],
        xlabel='dataset sizes',
        title='around vs rint',
        layout_sizes=[
            dict(label='VGA', width=640, height=480),
            dict(label='SVGA', width=800, height=600),
            dict(label='XGA', width=1024, height=768),
            dict(label='HD 720p', width=1280, height=960),
        ]
    )
    bm.run()
    bm.plot()
    bm.save_as_html(filepath='plot2.html')
    bm.save_as_png(filepath='plot2.png')


if __name__ == '__main__':
    main()
