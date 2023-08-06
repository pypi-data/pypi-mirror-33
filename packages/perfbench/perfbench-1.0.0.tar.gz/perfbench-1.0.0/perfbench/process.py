#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import timeit
import itertools
import math
import subprocess
import json
import warnings
import plotly
from IPython.core.magics.execution import TimeitResult
from . import utils
from . import plotly_utils
from . import _validators


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


def _bench(datasets, dataset_sizes, kernels, number=0, repeat=0, disable_tqdm=False):
    if repeat == 0:
        default_repeat = 7 if timeit.default_repeat < 7 else timeit.default_repeat
        repeat = default_repeat

    shape = (len(kernels), len(datasets))
    res = utils.create_empty_array_of_shape(shape)
    for i, j in itertools.product(range(shape[0]), range(shape[1])):
        res[i][j] = []

    for i, dataset in enumerate(tqdm(datasets, disable=disable_tqdm)):
        s_stmt = dataset.get('stmt')
        old_s_stmt = dataset.get('func')
        if old_s_stmt is not None:
            warnings.warn('`func` is deprecated. Use `stmt`.')
            s_stmt = old_s_stmt

        for j, dataset_size in enumerate(tqdm(dataset_sizes, disable=disable_tqdm)):
            data = s_stmt(dataset_size)
            for k, kernel in enumerate(kernels):
                k_stmt = kernel.get('stmt')
                old_k_stmt = kernel.get('func')
                if old_k_stmt is not None:
                    warnings.warn('`func` is deprecated. Use `stmt`.')
                    k_stmt = old_k_stmt

                timer = timeit.Timer(stmt=lambda: k_stmt(data))
                loops = number if number > 0 else _determine_number(timer)

                all_runs = timer.repeat(repeat=repeat, number=loops)
                best = min(all_runs) / loops
                worst = max(all_runs) / loops

                res[k][i].append(TimeitResult(loops, repeat, best, worst, all_runs, 0, 3))

    return res


class NotReadyError(Exception):
    pass


class Benchmark(object):

    def __init__(
            self, *,
            datasets,
            dataset_sizes,
            kernels,
            number=0,
            repeat=0,
            xlabel=None,
            title=None,
            layout_sizes=None
    ):
        self._datasets = datasets
        _validators.validate_datasets(self._datasets)

        self._dataset_sizes = dataset_sizes
        _validators.validate_dataset_sizes(self._dataset_sizes)

        self._kernels = kernels
        _validators.validate_kernels(self._kernels)

        self._number = number
        self._repeat = repeat
        self._xlabel = '' if xlabel is None else xlabel
        self._title = '' if title is None else title

        self._layout_sizes = None
        if layout_sizes is not None:
            self._layout_sizes = [dict(label='auto')] + layout_sizes
            _validators.validate_layout_sizes(self._layout_sizes)

        self._figure = None

    def run(self, *, disable_tqdm=False):
        results = _bench(
            datasets=self._datasets,
            dataset_sizes=self._dataset_sizes,
            kernels=self._kernels,
            number=self._number,
            repeat=self._repeat,
            disable_tqdm=disable_tqdm
        )
        self._figure = self._create_figure(benchmark_results=results)

    @classmethod
    def _default_colors(cls):
        return plotly.colors.DEFAULT_PLOTLY_COLORS

    @classmethod
    def _color(cls, *, index):
        colors = cls._default_colors()
        return colors[index % len(colors)]

    @staticmethod
    def _axis_range(sequence, use_log_scale=False):
        ar = [min(sequence), max(sequence)]
        if use_log_scale:
            ar[0] = math.log10(ar[0])
            ar[1] = math.log10(ar[1])
        return ar

    @staticmethod
    def _label_rgba(colors):
        return 'rgba({}, {}, {}, {})'.format(colors[0], colors[1], colors[2], colors[3])

    @staticmethod
    def _calc_filled_line(x, y, delta):
        x_rev = x[::-1]
        y_upper = [a + b for a, b in zip(y, delta)]
        y_lower = [a - b for a, b in zip(y, delta)]
        y_lower = y_lower[::-1]
        return x+x_rev, y_upper+y_lower

    @staticmethod
    def _create_update_menus(
            layout,
            layout_sizes=None,
            has_multiple_subplots=False
    ):
        updatemenus = []
        pos_x = 0.0

        if layout_sizes is not None:
            updatemenus.append(
                dict(
                    active=0,
                    buttons=plotly_utils.make_layout_size_buttons(datasets=layout_sizes),
                    direction='down',
                    showactive=True,
                    x=pos_x,
                    xanchor='left',
                    y=1.2,
                    yanchor='top'
                )
            )
            pos_x += 0.1

        updatemenus.append(
            dict(
                active=3,
                buttons=plotly_utils.make_scale_buttons(layout=layout),
                direction='down',
                showactive=True,
                x=pos_x,
                xanchor='left',
                y=1.2,
                yanchor='top'
            )
        )
        pos_x += 0.1

        if has_multiple_subplots:
            updatemenus.append(
                dict(
                    active=0,
                    buttons=plotly_utils.make_subplot_buttons(layout=layout),
                    direction='down',
                    showactive=True,
                    x=pos_x,
                    xanchor='left',
                    y=1.2,
                    yanchor='top'
                )
            )

        return updatemenus

    def _create_figure(self, *, benchmark_results):
        '''Create a figure with multiple subplots.'''
        ndatasets = len(self._datasets)
        subplots = plotly.tools.make_subplots(
            rows=ndatasets,
            cols=1,
            shared_xaxes=True,
            subplot_titles=[dataset.get('title', '') for dataset in self._datasets],
            print_grid=False
        )
        fig = plotly.graph_objs.FigureWidget(subplots)

        # for averages.
        for i, result in enumerate(benchmark_results):
            legendgroup = str(i)
            name = self._kernels[i].get('label', '')
            color = self._color(index=i)
            for j, item in enumerate(result):
                index = j + 1
                x = self._dataset_sizes
                y = [tres.average for tres in item]

                if ndatasets > 1:
                    title = self._datasets[j].get('title', '')
                    suffix = ' - ' + title if title else ''
                else:
                    suffix = ''

                trace = plotly.graph_objs.Scatter(
                    x=x,
                    y=y,
                    name=name + suffix,
                    text=[tres.__str__() for tres in item],
                    hoverinfo='x+text+name',
                    showlegend=True,
                    legendgroup=legendgroup,
                    line=dict(color=color)
                )
                fig.add_trace(trace, row=index, col=1)

        # for standard deviations.
        for i, result in enumerate(benchmark_results):
            legendgroup = str(i)
            color = self._color(index=i)
            for j, item in enumerate(result):
                index = j + 1
                x = self._dataset_sizes
                y = [tres.average for tres in item]
                fillcolor = self._label_rgba(colors=plotly.colors.unlabel_rgb(color) + (0.1,))
                fx, fy = self._calc_filled_line(x=x, y=y, delta=[tres.stdev for tres in item])
                trace = plotly.graph_objs.Scatter(
                    x=fx,
                    y=fy,
                    hoverinfo='x',
                    showlegend=False,
                    legendgroup=legendgroup,
                    line=dict(color='rgba(255,255,255,0)'),
                    fill='tozerox',
                    fillcolor=fillcolor
                )
                fig.add_trace(trace, row=index, col=1)

        # update the layout.
        layout = fig.layout

        layout.xaxis1.update(
            title=self._xlabel,
            type='log',
            autorange=True
        )
        for i, _ in enumerate(self._datasets):
            yaxis = 'yaxis' + str(i + 1)
            layout[yaxis].update(
                title='processing time',
                type='log',
                autorange=True
            )

        layout.title = self._title
        layout.updatemenus = self._create_update_menus(
            layout=layout,
            layout_sizes=self._layout_sizes,
            has_multiple_subplots=ndatasets > 1
        )

        return fig

    def plot(self, *, auto_open=True):
        '''Create a graph locally as an HTML document.

        Args:
            auto_open: If True, open the saved file in a web browser after saving.
        '''
        if self._figure is None:
            raise NotReadyError('Benchmark results are not ready yet.')

        if utils.is_interactive():
            plotly.offline.init_notebook_mode()
            plotly.offline.iplot(self._figure, show_link=False)
        else:
            plotly.offline.plot(self._figure, show_link=False, auto_open=auto_open)

    def save_as_html(self, *, filepath='temp-plot.html'):
        '''Save as a html.

        Args:
            filepath: The local filepath to save the outputted chart to.
                If the filepath already exists, it will be overwritten.
        '''
        if self._figure is None:
            raise NotReadyError('Benchmark results are not ready yet.')

        plotly.offline.plot(self._figure, show_link=False, auto_open=False, filename=filepath)

    def save_as_png(self, *, filepath='plot_image.png', width=1280, height=960):
        '''Save as a png.

        Args:
            filepath: The local filepath to save the image to.
            width: Specifies the width of the image in `px`.
            height: Specifies the height of the image in `px`.

        Returns:
            True if successful, false otherwise.
        '''
        if not utils.cmd_exists('orca'):
            warnings.warn('`orca` is not installed, this function can not be used.')
            return False

        dirpath, filename = os.path.split(filepath)
        if not dirpath:
            dirpath = '.'

        if self._figure is None:
            raise NotReadyError('Benchmark results are not ready yet.')

        dumps = json.dumps(self._figure, cls=plotly.utils.PlotlyJSONEncoder)
        try:
            subprocess.check_call([
                'orca',
                'graph', dumps,
                '-d', dirpath,
                '-o', filename,
                '--width', str(width),
                '--height', str(height)
            ])
            return True
        except subprocess.CalledProcessError:
            return False
