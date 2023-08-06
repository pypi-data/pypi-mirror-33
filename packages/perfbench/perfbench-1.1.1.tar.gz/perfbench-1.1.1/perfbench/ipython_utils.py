#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# - Copyright (c) 2008-Present, IPython Development Team
# - Copyright (c) 2001-2007, Fernando Perez <fernando.perez@colorado.edu>
# - Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
# - Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import math


class TimeitResult(object):
    '''Object returned by the timeit magic with info about the run.

    Args:
        loops (int): Number of loops done per measurement.
        repeat (int): Number of times the measurement has been repeated.
        all_runs (list(float)): Execution time of each run (in seconds).
        precision: number of significant digits.
    '''
    def __init__(self, *, loops, repeat, all_runs, precision=3):
        self._loops = loops
        self._repeat = repeat
        self._best = min(all_runs) / loops
        self._worst = max(all_runs) / loops
        timings = [dt / loops for dt in all_runs]
        self._average = math.fsum(timings) / len(timings)
        self._stdev = math.sqrt(math.fsum([(x - self._average) ** 2 for x in timings]) / len(timings))
        self._precision = precision

    @property
    def loops(self):
        return self._loops

    @property
    def repeat(self):
        return self._repeat

    @property
    def best(self):
        return self._best

    @property
    def worst(self):
        return self._worst

    @property
    def average(self):
        return self._average

    @property
    def stdev(self):
        return self._stdev

    def __str__(self):
        fmt = '{mean} {pm} {stdev} per loop (mean {pm} s.d. of {runs} run{run_plural}, {loops} loop{loop_plural} each)'
        return fmt.format(
            mean=_format_time(timespan=self.average, precision=self._precision),
            pm='\xb1',
            stdev=_format_time(timespan=self.stdev, precision=self._precision),
            runs=self.repeat,
            run_plural='s' if self.repeat > 1 else '',
            loops=self.loops,
            loop_plural='s' if self.loops > 1 else ''
        )


def _seconds_to_hrf(seconds, separator=' '):
    '''Convert seconds to human readable format.

    Args:
        seconds (int): seconds to convert.
        separator (str): separator.

    Returns:
        str: Human readable format.
    '''
    parts = [
        ('w', 60 * 60 * 24 * 7),
        ('d', 60 * 60 * 24),
        ('h', 60 * 60),
        ('m', 60),
        ('s', 1)
    ]

    time = []
    leftover = seconds
    for suffix, length in parts:
        value = int(leftover / length)
        if value > 0:
            leftover %= length
            time.append('{}{}'.format(str(value), suffix))
        if leftover < 1:
            break

    return separator.join(time)


def _format_time(timespan, precision=3):
    if timespan > 60.0:
        return _seconds_to_hrf(timespan)

    units = ('s', 'ms', '\xb5s', 'ns')
    scaling = (1, 1e+3, 1e+6, 1e+9)
    if timespan > 0.0:
        order = min(max(-int(math.floor(math.log10(timespan)) // 3), 0), 3)
    else:
        order = 3

    return '{0:.{1}g} {2}'.format(timespan * scaling[order], precision, units[order])


def determine_number(timer):
    '''Determine number so that 0.2 <= total time < 2.0'''
    number = 0
    for index in range(0, 10):
        number = 10 ** index
        time_number = timer.timeit(number=number)
        if time_number >= 0.2:
            break

    return number
