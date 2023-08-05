#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import timeit
import itertools
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
        self.xaxis_type = 'log' if logx else 'category'
        self.results = None

    def run(self):

        self.results = _bench(setups=self.setups,
                              kernels=self.kernels,
                              ntimes=self.ntimes,
                              number=self.number,
                              repeat=self.repeat)

    def _figure(self):

        if len(self.setups) > 1:
            fig = plotly.tools.make_subplots(
                rows=len(self.setups),
                cols=1,
                shared_xaxes=True,
                subplot_titles=[setup.get('title', '') for setup in self.setups]
            )

            for i, result in enumerate(self.results):
                for j, item in enumerate(result):
                    name = self.setups[i].get('title', '') + ' - ' + self.kernels[j].get('label', '')
                    trace = plotly.graph_objs.Scatter(
                        x=self.ntimes,
                        y=[tres.average for tres in item],
                        text=[tres.__str__() for tres in item],
                        hoverinfo='text',
                        name=name,
                        legendgroup=str(i)
                    )
                    index = i + 1
                    fig.append_trace(trace, index, 1)
                    xaxis = 'xaxis' + str(index)
                    yaxis = 'yaxis' + str(index)
                    fig['layout'][xaxis].update(title=self.xlabel, type=self.xaxis_type, autorange=True)
                    fig['layout'][yaxis].update(title='processing time', type='log', autorange=True)

            fig['layout'].update(title=self.title)

            return fig

        else:

            for result in self.results:
                data = []
                for index, item in enumerate(result):
                    trace = plotly.graph_objs.Scatter(
                        x=self.ntimes,
                        y=[tres.average for tres in item],
                        text=[tres.__str__() for tres in item],
                        hoverinfo='text',
                        name=self.kernels[index].get('label', '')
                    )
                    data.append(trace)

            layout = plotly.graph_objs.Layout(
                title=self.title,
                xaxis={
                    'title': self.xlabel,
                    'type': self.xaxis_type,
                    'autorange': True,
                },
                yaxis={
                    'title': 'processing time',
                    'type': 'log',
                    'autorange': True,
                }
            )

            return plotly.graph_objs.Figure(data=data, layout=layout)

    def show(self):
        fig = self._figure()
        if utils.is_interactive():
            plotly.offline.init_notebook_mode()
            plotly.offline.iplot(fig, show_link=False)
        else:
            plotly.offline.plot(fig, show_link=False)
