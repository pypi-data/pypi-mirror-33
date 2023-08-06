#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import os
import sys
sys.path.append('../')
from perfbench.process import *


class TestBenchmark(TestCase):
    def test__default_colors(self):
        actual = Benchmark._default_colors()
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(len(actual) > 0)

    def test__color(self):
        actual = Benchmark._color(index=0)
        self.assertTrue(isinstance(actual, str))

    def test__axis_range(self):
        actual = Benchmark._axis_range(sequence=[1, 10, 100])
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(actual == [1, 100])

        actual = Benchmark._axis_range(sequence=[1, 10, 100], use_log_scale=True)
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(actual == [0, 2])

    def test__label_rgba(self):
        actual = Benchmark._label_rgba(colors=(32, 64, 128, 0.5))
        self.assertTrue(isinstance(actual, str))
        self.assertTrue(actual == 'rgba(32, 64, 128, 0.5)')

    def test_plot(self):
        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [i for i in range(n)], title='')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
                dict(stmt=lambda x: [value * 2 for value in x], label='multiply')
            ],
            xlabel='dataset sizes',
            title='test'
        )
        bm.run(disable_tqdm=True)
        bm.plot(auto_open=False)

        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [int(i) for i in range(n)], title='int'),
                dict(stmt=lambda n: [float(i) for i in range(n)], title='float')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
                dict(stmt=lambda x: [value * 2 for value in x], label='multiply')
            ],
            xlabel='dataset sizes',
            title='test'
        )
        bm.run(disable_tqdm=True)
        bm.plot(auto_open=False)

    def test_save_as_html(self):
        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [i for i in range(n)], title='')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
                dict(stmt=lambda x: [value * 2 for value in x], label='multiply')
            ],
            xlabel='dataset sizes',
            title='test'
        )
        bm.run(disable_tqdm=True)
        bm.save_as_html(filepath='test.html')
        self.assertTrue(os.path.exists('./test.html'))

    def test_save_as_png(self):
        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [i for i in range(n)], title='')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
                dict(stmt=lambda x: [value * 2 for value in x], label='multiply')
            ],
            xlabel='dataset sizes',
            title='test'
        )
        bm.run(disable_tqdm=True)
        ret = bm.save_as_png(filepath='test.png')
        self.assertTrue(ret)
        #self.assertTrue(os.path.exists('./test.png'))

    def test_layout_sizes(self):
        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [i for i in range(n)], title='')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
                dict(stmt=lambda x: [value * 2 for value in x], label='multiply')
            ],
            xlabel='dataset sizes',
            title='test',
            layout_sizes=[
                dict(label='VGA', width=640, height=480),
                dict(label='SVGA', width=800, height=600),
                dict(label='XGA', width=1024, height=768),
                dict(label='HD 720p', width=1280, height=960),
            ]
        )
        bm.run(disable_tqdm=True)
        bm.plot(auto_open=False)

        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [int(i) for i in range(n)], title='int'),
                dict(stmt=lambda n: [float(i) for i in range(n)], title='float')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
                dict(stmt=lambda x: [value * 2 for value in x], label='multiply')
            ],
            xlabel='dataset sizes',
            title='test',
            layout_sizes=[
                dict(label='VGA', width=640, height=480),
                dict(label='SVGA', width=800, height=600),
                dict(label='XGA', width=1024, height=768),
                dict(label='HD 720p', width=1280, height=960),
            ]
        )
        bm.run(disable_tqdm=True)
        bm.plot(auto_open=False)

    def test_results_are_not_ready(self):
        bm = Benchmark(
            datasets=[
                dict(stmt=lambda n: [i for i in range(n)], title='')
            ],
            dataset_sizes=[2 ** n for n in range(2)],
            kernels=[
                dict(stmt=lambda x: [value + 2 for value in x], label='add'),
            ],
            xlabel='dataset sizes',
            title='test',
        )

        with self.assertRaises(NotReadyError):
            bm.plot(auto_open=False)

        with self.assertRaises(NotReadyError):
            bm.save_as_html(filepath='test.html')

        with self.assertRaises(NotReadyError):
            bm.save_as_png(filepath='test.png')
