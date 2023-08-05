#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import timeit
import itertools
import math
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
        time_number = timer.timeit(number)
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
        for j, ntime in enumerate(tqdm(ntimes)):
            sfn = setup.get('func')
            data = sfn(ntime)
            for k, kernel in enumerate(kernels):
                kfn = kernel.get('func')
                timer = timeit.Timer(stmt=lambda: kfn(data))
                loops = number if number > 0 else _determine_number(timer)

                all_runs = timer.repeat(repeat, loops)
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
        self.setups = setups
        self.kernels = kernels
        self.ntimes = ntimes
        self.number = number
        self.repeat = repeat
        self.xlabel = '' if xlabel is None else xlabel
        self.title = '' if title is None else title
        self.logx = logx
        self.xaxis_type = 'log' if logx else 'category'
        self.results = None

    def run(self):

        self.results = _bench(setups=self.setups,
                              kernels=self.kernels,
                              ntimes=self.ntimes,
                              number=self.number,
                              repeat=self.repeat)

    @property
    def _colors(self):
        return plotly.colors.DEFAULT_PLOTLY_COLORS

    @property
    def _xaxis_type(self):
        return 'log' if self.logx else '-'

    @property
    def _xaxis_range(self):
        axis_range = [min(self.ntimes), max(self.ntimes)]
        if self.logx:
            axis_range[0] = math.log10(axis_range[0])
            axis_range[1] = math.log10(axis_range[1])
        return axis_range

    @classmethod
    def _label_rgba(cls, colors):
        return 'rgba({}, {}, {}, {})'.format(colors[0], colors[1], colors[2], colors[3])

    @classmethod
    def _make_filled_line(cls, x, y, delta, fillcolor):
        x_rev = x[::-1]
        y_upper = [a + b for a, b in zip(y, delta)]
        y_lower = [a - b for a, b in zip(y, delta)]
        y_lower = y_lower[::-1]
        trace = plotly.graph_objs.Scatter(
            x=x+x_rev,
            y=y_upper+y_lower,
            showlegend=False,
            hoverinfo='x',
            line=dict(color='rgba(255,255,255,0)'),
            fill='tozerox',
            fillcolor=fillcolor
        )
        return trace

    def _plot(self):
        colors = self._colors
        ncolors = len(colors)

        for result in self.results:
            data = []
            for index, item in enumerate(result):
                averages = [tres.average for tres in item]
                color = colors[index % ncolors]
                trace = plotly.graph_objs.Scatter(
                    x=self.ntimes,
                    y=averages,
                    text=[tres.__str__() for tres in item],
                    hoverinfo='x+text+name',
                    name=self.kernels[index].get('label', ''),
                    line=dict(color=color)
                )
                data.append(trace)
                #
                stdevs = [tres.stdev for tres in item]
                fillcolor = self._label_rgba(plotly.colors.unlabel_rgb(color) + (0.2,))
                trace = self._make_filled_line(
                    x=self.ntimes,
                    y=averages,
                    delta=stdevs,
                    fillcolor=fillcolor
                )
                data.append(trace)

        layout = plotly.graph_objs.Layout(
            title=self.title,
            xaxis={
                'title': self.xlabel,
                'type': self._xaxis_type,
                'range': self._xaxis_range,
            },
            yaxis={
                'title': 'processing time',
                'type': 'log',
                'autorange': True,
            }
        )

        return plotly.graph_objs.Figure(data=data, layout=layout)

    def _multiplot(self):
        colors = self._colors
        ncolors = len(colors)

        fig = plotly.tools.make_subplots(
            rows=len(self.setups),
            cols=1,
            shared_xaxes=True,
            subplot_titles=[setup.get('title', '') for setup in self.setups]
        )
        for i, result in enumerate(self.results):
            index = i + 1
            for j, item in enumerate(result):
                name = self.setups[i].get('title', '') + ' - ' + self.kernels[j].get('label', '')
                averages = [tres.average for tres in item]
                color = colors[j % ncolors]
                trace = plotly.graph_objs.Scatter(
                    x=self.ntimes,
                    y=averages,
                    text=[tres.__str__() for tres in item],
                    hoverinfo='x+text+name',
                    name=name,
                    legendgroup=str(i),
                    line=dict(color=color)
                )
                fig.append_trace(trace, index, 1)
                #
                stdevs = [tres.stdev for tres in item]
                fillcolor = self._label_rgba(plotly.colors.unlabel_rgb(color) + (0.2,))
                trace = self._make_filled_line(
                    x=self.ntimes,
                    y=averages,
                    delta=stdevs,
                    fillcolor=fillcolor
                )
                fig.append_trace(trace, index, 1)

                xaxis = 'xaxis' + str(index)
                yaxis = 'yaxis' + str(index)
                fig['layout'][xaxis].update(
                    title=self.xlabel,
                    type=self._xaxis_type,
                    range=self._xaxis_range
                )
                fig['layout'][yaxis].update(
                    title='processing time',
                    type='log',
                    autorange=True
                )

        fig['layout'].update(title=self.title)

        return fig

    def show(self):
        '''for backward compatibility.'''
        warnings.warn('This function will be removed soon.')
        self.plot()

    def plot(self, *, auto_open=True):
        fig = self._multiplot() if len(self.setups) > 1 else self._plot()
        if utils.is_interactive():
            plotly.offline.init_notebook_mode()
            plotly.offline.iplot(fig, show_link=False)
        else:
            plotly.offline.plot(fig, show_link=False, auto_open=auto_open)
