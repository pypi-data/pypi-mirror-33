#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import timeit
import itertools
import math
import subprocess
import json
import warnings
import plotly
from IPython.core.magics.execution import TimeitResult
from . import utils


try:
    if utils.is_interactive():
        from tqdm import tqdm_notebook as tqdm
    else:
        from tqdm import tqdm

except ImportError:
    tqdm = lambda x: x


def _determine_number(timer):
    '''Determine number so that 0.2 <= total time < 2.0'''
    number = 0
    for index in range(0, 10):
        number = 10 ** index
        time_number = timer.timeit(number=number)
        if time_number >= 0.2:
            break

    return number


def _bench(setups, kernels, ntimes, number=0, repeat=0):
    if repeat == 0:
        default_repeat = 7 if timeit.default_repeat < 7 else timeit.default_repeat
        repeat = default_repeat

    shape = (len(setups), len(kernels))
    res = utils.create_empty_array_of_shape(shape)
    for i, j in itertools.product(range(shape[0]), range(shape[1])):
        res[i][j] = []

    for i, setup in enumerate(tqdm(setups)):
        sfn = setup.get('func')
        for j, ntime in enumerate(tqdm(ntimes)):
            data = sfn(ntime)
            for k, kernel in enumerate(kernels):
                kfn = kernel.get('func')
                timer = timeit.Timer(stmt=lambda: kfn(data))
                loops = number if number > 0 else _determine_number(timer)

                all_runs = timer.repeat(repeat=repeat, number=loops)
                best = min(all_runs) / loops
                worst = max(all_runs) / loops

                res[i][k].append(TimeitResult(loops, repeat, best, worst, all_runs, 0, 3))

    return res


class Benchmark(object):

    def __init__(self, *,
                 setups,
                 kernels,
                 ntimes,
                 number=0,
                 repeat=0,
                 xlabel=None,
                 title=None,
                 logx=False):
        self._setups = setups
        self._kernels = kernels
        self._ntimes = ntimes
        self._number = number
        self._repeat = repeat
        self._xlabel = '' if xlabel is None else xlabel
        self._title = '' if title is None else title
        self._logx = logx
        self._results = None

    def run(self):
        self._results = _bench(
            setups=self._setups,
            kernels=self._kernels,
            ntimes=self._ntimes,
            number=self._number,
            repeat=self._repeat
        )

    @property
    def _xaxis_type(self):
        return 'log' if self._logx else '-'

    @classmethod
    def _default_colors(cls):
        return plotly.colors.DEFAULT_PLOTLY_COLORS

    @classmethod
    def _color(cls, *, index):
        colors = cls._default_colors()
        return colors[index % len(colors)]

    @classmethod
    def _axis_range(cls, *, sequence, is_log_scale=False):
        ar = [min(sequence), max(sequence)]
        if is_log_scale:
            ar[0] = math.log10(ar[0])
            ar[1] = math.log10(ar[1])
        return ar

    @classmethod
    def _label_rgba(cls, *, colors):
        return 'rgba({}, {}, {}, {})'.format(colors[0], colors[1], colors[2], colors[3])

    @classmethod
    def _make_filled_line(cls, *, x, y, delta, legendgroup, fillcolor):
        x_rev = x[::-1]
        y_upper = [a + b for a, b in zip(y, delta)]
        y_lower = [a - b for a, b in zip(y, delta)]
        y_lower = y_lower[::-1]
        trace = plotly.graph_objs.Scatter(
            x=x+x_rev,
            y=y_upper+y_lower,
            hoverinfo='x',
            showlegend=False,
            legendgroup=legendgroup,
            line=dict(color='rgba(255,255,255,0)'),
            fill='tozerox',
            fillcolor=fillcolor
        )
        return trace

    def _create_figure(self):
        '''Create a figure.'''
        if len(self._setups) > 1:
            return self._create_figure_with_multiple_subplots()

        for result in self._results:
            data = []
            for index, item in enumerate(result):
                x = self._ntimes
                y = [tres.average for tres in item]
                legendgroup = str(index)

                color = self._color(index=index)
                trace = plotly.graph_objs.Scatter(
                    x=x,
                    y=y,
                    name=self._kernels[index].get('label', ''),
                    text=[tres.__str__() for tres in item],
                    hoverinfo='x+text+name',
                    showlegend=True,
                    legendgroup=legendgroup,
                    line=dict(color=color),
                )
                data.append(trace)

                fillcolor = self._label_rgba(colors=plotly.colors.unlabel_rgb(color) + (0.2,))
                trace = self._make_filled_line(
                    x=x,
                    y=y,
                    delta=[tres.stdev for tres in item],
                    legendgroup=legendgroup,
                    fillcolor=fillcolor
                )
                data.append(trace)

        layout = plotly.graph_objs.Layout(
            title=self._title,
            xaxis=dict(
                title=self._xlabel,
                type=self._xaxis_type,
                range=self._axis_range(sequence=x, is_log_scale=self._logx)
            ),
            yaxis=dict(
                title='processing time',
                type='log',
                autorange=True
            )
        )

        return plotly.graph_objs.Figure(data=data, layout=layout)

    def _create_figure_with_multiple_subplots(self):
        '''Create a figure with multiple subplots.'''
        fig = plotly.tools.make_subplots(
            rows=len(self._setups),
            cols=1,
            shared_xaxes=True,
            subplot_titles=[setup.get('title', '') for setup in self._setups]
        )
        for i, result in enumerate(self._results):
            index = i + 1
            showlegend = True if i == 0 else False
            for j, item in enumerate(result):
                x = self._ntimes
                y = [tres.average for tres in item]
                legendgroup = str(j)

                color = self._color(index=j)
                trace = plotly.graph_objs.Scatter(
                    x=x,
                    y=y,
                    name=self._kernels[j].get('label', ''),
                    text=[tres.__str__() for tres in item],
                    hoverinfo='x+text+name',
                    showlegend=showlegend,
                    legendgroup=legendgroup,
                    line=dict(color=color)
                )
                fig.append_trace(trace, index, 1)

                fillcolor = self._label_rgba(colors=plotly.colors.unlabel_rgb(color) + (0.2,))
                trace = self._make_filled_line(
                    x=x,
                    y=y,
                    delta=[tres.stdev for tres in item],
                    legendgroup=legendgroup,
                    fillcolor=fillcolor
                )
                fig.append_trace(trace, index, 1)

                xaxis = 'xaxis' + str(index)
                yaxis = 'yaxis' + str(index)
                fig['layout'][xaxis].update(
                    title=self._xlabel,
                    type=self._xaxis_type,
                    range=self._axis_range(sequence=x, is_log_scale=self._logx)
                )
                fig['layout'][yaxis].update(
                    title='processing time',
                    type='log',
                    autorange=True
                )

        fig['layout'].update(title=self._title)

        return fig

    def show(self):
        '''for backward compatibility.'''
        warnings.warn('This function will be removed soon.')
        self.plot()

    def plot(self, *, auto_open=True):
        fig = self._create_figure()
        if utils.is_interactive():
            plotly.offline.init_notebook_mode()
            plotly.offline.iplot(fig, show_link=False)
        else:
            plotly.offline.plot(fig, show_link=False, auto_open=auto_open)

    def save_as_html(self, *, filepath='temp-plot.html'):
        fig = self._create_figure()
        plotly.offline.plot(fig, show_link=False, auto_open=False, filename=filepath)

    def save_as_png(self, *, filepath='plot_image.png'):
        if not utils.cmd_exists('orca'):
            warnings.warn('`orca` is not installed, this function can not be used.')
            return False

        fig = self._create_figure()
        dumps = json.dumps(fig)
        try:
            subprocess.check_call(['orca', 'graph', dumps, '-o', filepath])
            return True
        except subprocess.CalledProcessError:
            return False
