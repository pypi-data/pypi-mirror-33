#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import sys
sys.path.append('../')
from perfbench.process import *


class TestBenchmark(TestCase):
    def test__colors(self):
        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(3)],
            xlabel='samples',
            title='test',
            logx=False
        )
        actual = bm._colors
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(len(actual) > 0)

    def test__xaxis_type(self):
        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(3)],
            xlabel='samples',
            title='test',
            logx=False
        )
        actual = bm._xaxis_type
        self.assertTrue(isinstance(actual, str))
        self.assertTrue(actual == '-')

        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(3)],
            xlabel='samples',
            title='test',
            logx=True
        )
        actual = bm._xaxis_type
        self.assertTrue(isinstance(actual, str))
        self.assertTrue(actual == 'log')

    def test__xaxis_range(self):
        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[1, 10, 100],
            xlabel='samples',
            title='test',
            logx=False
        )
        actual = bm._xaxis_range
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(actual == [1, 100])

        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[1, 10, 100],
            xlabel='samples',
            title='test',
            logx=True
        )
        actual = bm._xaxis_range
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(actual == [0, 2])

    def test__label_rgba(self):
        actual = Benchmark._label_rgba((32, 64, 128, 0.5))
        self.assertTrue(isinstance(actual, str))
        self.assertTrue(actual == 'rgba(32, 64, 128, 0.5)')

    def test_plot(self):
        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(2)],
            xlabel='samples',
            title='test',
            logx=False
        )
        bm.run()
        bm.plot(auto_open=False)

        bm = Benchmark(
            setups=[
                dict(func=lambda n: [i for i in range(n)], title='')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(2)],
            xlabel='samples',
            title='test',
            logx=False
        )
        bm.run()
        bm.plot(auto_open=False)

    def test_multiplot(self):
        bm = Benchmark(
            setups=[
                dict(func=lambda n: [int(i) for i in range(n)], title='int'),
                dict(func=lambda n: [float(i) for i in range(n)], title='float')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(2)],
            xlabel='samples',
            title='test',
            logx=False
        )
        bm.run()
        bm.plot(auto_open=False)

        bm = Benchmark(
            setups=[
                dict(func=lambda n: [int(i) for i in range(n)], title='int'),
                dict(func=lambda n: [float(i) for i in range(n)], title='float')
            ],
            kernels=[
                dict(func=lambda x: [value + 2 for value in x], label='add'),
                dict(func=lambda x: [value * 2 for value in x], label='multiply')
            ],
            ntimes=[2 ** n for n in range(2)],
            xlabel='samples',
            title='test',
            logx=True
        )
        bm.run()
        bm.plot(auto_open=False)
