#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import itertools
from collections import namedtuple


try:
    from math import gcd
except ImportError:
    # for backward compatibility.
    def _gcd(a, b):
        '''Greatest Common Divisor.'''
        while b:
            a, b = b, a % b
        return a

    gcd = _gcd


def _glab_keys(d, pattern):
    prog = re.compile(pattern)
    ret = [key for key in d.keys() if prog.match(key)]
    ret.sort()
    return ret


def _grab_attributes(obj, pattern):
    prog = re.compile(pattern)
    ret = [attr for attr in dir(obj) if prog.match(attr)]
    ret.sort()
    return ret


def _contains_free_anchor(layout, axes):
    for axis in axes:
        if layout[axis].anchor == 'free':
            return True

    return False


def _find_axes_combs(layout):
    '''Find axes combinations.'''
    xaxes = _grab_attributes(layout, r'^xaxis[0-9]*')
    n_xaxes = len(xaxes)
    if n_xaxes == 0:
        raise ValueError('xaxes not contained in layout')

    yaxes = _grab_attributes(layout, r'^yaxis[0-9]*')
    n_yaxes = len(yaxes)
    if n_yaxes == 0:
        raise ValueError('yaxes not contained in layout')

    is_shared_xaxes = _contains_free_anchor(layout, yaxes)
    is_shared_yaxes = _contains_free_anchor(layout, xaxes)

    if is_shared_xaxes and is_shared_yaxes:
        xaxes = xaxes * n_yaxes
        yaxes = yaxes * n_xaxes
    else:
        coef = gcd(n_xaxes, n_yaxes)
        xaxes = xaxes * (n_yaxes // coef)
        yaxes = yaxes * (n_xaxes // coef)

    if is_shared_yaxes:
        yaxes.sort()

    return [(xaxis, yaxis) for xaxis, yaxis in zip(xaxes, yaxes)]


def make_subplot_buttons(layout):
    '''Make subplot buttons.'''
    buttons = []

    combs = _find_axes_combs(layout)

    # labels
    annotations = layout.annotations
    if annotations is None:
        annotations = []

    button_labels = ['all', ]
    if annotations:
        for i, annotation in enumerate(itertools.zip_longest(combs, annotations)):
            if annotation[1] is None:
                button_labels.append('subplot{}'.format(i + 1))
            else:
                button_labels.append(annotation[1].text)
    else:
        for i, _ in enumerate(combs):
            button_labels.append('subplot{}'.format(i + 1))

    # all
    args = [dict(visible=[True for _ in combs]), ]

    arg = {}

    for i, annotation in enumerate(annotations):
        s = 'annotations[{}]'.format(i)
        arg[s + '.visible'] = True
        arg[s + '.x'] = annotation.x
        arg[s + '.y'] = annotation.y

    for comb in combs:
        src_xaxis, src_yaxis = comb
        dst_xaxis = 'xaxis' if src_xaxis == 'xaxis1' else src_xaxis
        dst_yaxis = 'yaxis' if src_yaxis == 'yaxis1' else src_yaxis

        arg[dst_xaxis + '.visible'] = True
        arg[dst_xaxis + '.domain'] = layout[src_xaxis].domain
        arg[dst_xaxis + '.position'] = layout[src_xaxis].position

        arg[dst_yaxis + '.visible'] = True
        arg[dst_yaxis + '.domain'] = layout[src_yaxis].domain
        arg[dst_yaxis + '.position'] = layout[src_yaxis].position

    args.append(arg)

    buttons.append(
        dict(
            label=button_labels[0],
            method='update',
            args=args
        )
    )

    # subplots
    for index, cur_cmb in enumerate(combs):
        args = [dict(visible=[True if i == index else False for i, _ in enumerate(combs)]), ]

        arg = {}

        for i, annotation in enumerate(annotations):
            s = 'annotations[{}]'.format(i)
            if i == index:
                arg[s + '.visible'] = True
                arg[s + '.x'] = 0.5
                arg[s + '.y'] = 1.0
            else:
                arg[s + '.visible'] = False

        for i, comb in enumerate(combs):
            src_xaxis, src_yaxis = comb
            dst_xaxis = 'xaxis' if src_xaxis == 'xaxis1' else src_xaxis
            dst_yaxis = 'yaxis' if src_yaxis == 'yaxis1' else src_yaxis

            if i == index:
                arg[dst_xaxis + '.visible'] = True
                arg[dst_xaxis + '.domain'] = [0.01, 1.0]
                arg[dst_xaxis + '.position'] = 0.0

                arg[dst_yaxis + '.visible'] = True
                arg[dst_yaxis + '.domain'] = [0.01, 1.0]
                arg[dst_yaxis + '.position'] = 0.0
            else:
                if src_xaxis != cur_cmb[0]:
                    arg[dst_xaxis + '.visible'] = False
                    arg[dst_xaxis + '.domain'] = [0.0, 0.01]

                if src_yaxis != cur_cmb[1]:
                    arg[dst_yaxis + '.visible'] = False
                    arg[dst_yaxis + '.domain'] = [0.0, 0.01]

        args.append(arg)

        buttons.append(
            dict(
                label=button_labels[index + 1],
                method='update',
                args=args
            )
        )

    return buttons


def make_scale_buttons(layout):
    '''Make scale buttons.'''
    Dataset = namedtuple('Dataset', ('xtype', 'ytype', 'label'))
    datasets = [
        Dataset(xtype='linear', ytype='linear', label='Linear'),
        Dataset(xtype='log', ytype='linear', label='Semilog-X'),
        Dataset(xtype='linear', ytype='log', label='Semilog-Y'),
        Dataset(xtype='log', ytype='log', label='Log')
    ]

    buttons = []

    combs = _find_axes_combs(layout)

    for dataset in datasets:
        xtype = dataset.xtype
        ytype = dataset.ytype
        label = dataset.label

        arg = {}
        for comb in combs:
            src_xaxis, src_yaxis = comb
            dst_xaxis = 'xaxis' if src_xaxis == 'xaxis1' else src_xaxis
            dst_yaxis = 'yaxis' if src_yaxis == 'yaxis1' else src_yaxis

            arg[dst_xaxis + '.type'] = xtype
            arg[dst_xaxis + '.autorange'] = True

            arg[dst_yaxis + '.type'] = ytype
            arg[dst_yaxis + '.autorange'] = True

        buttons.append(
            dict(
                label=label,
                method='relayout',
                args=[arg]
            )
        )

    return buttons


def make_layout_size_buttons(layout_sizes):
    '''Make layout size buttons.'''
    buttons = []

    for layout_size in layout_sizes:
        label = layout_size.label
        width = layout_size.width
        height = layout_size.height

        arg = dict(
            autosize=True if width is None or height is None else False,
            width=0 if width is None else width,
            height=0 if height is None else height
        )

        buttons.append(
            dict(
                label=label,
                method='relayout',
                args=[arg]
            )
        )

    return buttons
