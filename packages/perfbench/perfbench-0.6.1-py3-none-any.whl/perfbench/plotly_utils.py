#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import itertools


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
    reobj = re.compile(pattern)
    res = []
    for key in d.keys():
        if reobj.match(key):
            res.append(key)
    res.sort()

    return res


def _contains_free_anchor(fig, axes):
    for axis in axes:
        anchor = fig.layout[axis].get('anchor')
        if anchor == 'free':
            return True

    return False


def _find_axes_combs(fig):
    xaxes = _glab_keys(fig.layout, r'^xaxis[0-9]{0,1}')
    yaxes = _glab_keys(fig.layout, r'^yaxis[0-9]{0,1}')

    is_shared_xaxes = _contains_free_anchor(fig, yaxes)
    is_shared_yaxes = _contains_free_anchor(fig, xaxes)

    n_xaxes = len(xaxes)
    n_yaxes = len(yaxes)
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


def make_subplot_buttons(fig):
    '''Make subplot buttons'''
    buttons = []

    combs = _find_axes_combs(fig)

    # labels
    annotations = fig.layout.get('annotations', [])
    button_labels = ['all', ]
    if annotations == []:
        for i, _ in enumerate(combs):
            button_labels.append('subplot{}'.format(i + 1))
    else:
        for i, annotation in enumerate(itertools.zip_longest(combs, annotations)):
            if annotation[1] is None:
                button_labels.append('subplot{}'.format(i + 1))
            else:
                button_labels.append(annotation[1]['text'])

    # all
    args = [dict(visible=[True for _ in combs]), ]

    temp = {}

    for i, annotation in enumerate(annotations):
        s = 'annotations[{}]'.format(i)
        temp[s + '.visible'] = True
        temp[s + '.x'] = annotation.get('x', 1.0)
        temp[s + '.y'] = annotation.get('y', 1.0)

    for comb in combs:
        src_xaxis, src_yaxis = comb
        dst_xaxis = 'xaxis' if src_xaxis == 'xaxis1' else src_xaxis
        dst_yaxis = 'yaxis' if src_yaxis == 'yaxis1' else src_yaxis

        temp[dst_xaxis + '.visible'] = True
        temp[dst_xaxis + '.domain'] = fig.layout[src_xaxis]['domain']
        temp[dst_xaxis + '.position'] = fig.layout[src_xaxis].get('position', 0.0)

        temp[dst_yaxis + '.visible'] = True
        temp[dst_yaxis + '.domain'] = fig.layout[src_yaxis]['domain']
        temp[dst_yaxis + '.position'] = fig.layout[src_yaxis].get('position', 0.0)

    args.append(temp)

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

        temp = {}

        for i, annotation in enumerate(annotations):
            s = 'annotations[{}]'.format(i)
            if i == index:
                temp[s + '.visible'] = True
                temp[s + '.x'] = 0.5
                temp[s + '.y'] = 1.0
            else:
                temp[s + '.visible'] = False

        for i, comb in enumerate(combs):
            src_xaxis, src_yaxis = comb
            dst_xaxis = 'xaxis' if src_xaxis == 'xaxis1' else src_xaxis
            dst_yaxis = 'yaxis' if src_yaxis == 'yaxis1' else src_yaxis

            if i == index:
                temp[dst_xaxis + '.visible'] = True
                temp[dst_xaxis + '.domain'] = [0.01, 1.0]
                temp[dst_xaxis + '.position'] = 0.0

                temp[dst_yaxis + '.visible'] = True
                temp[dst_yaxis + '.domain'] = [0.01, 1.0]
                temp[dst_yaxis + '.position'] = 0.0
            else:
                if src_xaxis != cur_cmb[0]:
                    temp[dst_xaxis + '.visible'] = False
                    temp[dst_xaxis + '.domain'] = [0.0, 0.01]

                if src_yaxis != cur_cmb[1]:
                    temp[dst_yaxis + '.visible'] = False
                    temp[dst_yaxis + '.domain'] = [0.0, 0.01]

        args.append(temp)

        buttons.append(
            dict(
                label=button_labels[index + 1],
                method='update',
                args=args
            )
        )

    return buttons


def make_scale_buttons(fig):

    datasets = [
        dict(label='Linear', xtype='linear', ytype='linear'),
        dict(label='Semilog-X', xtype='log', ytype='linear'),
        dict(label='Semilog-Y', xtype='linear', ytype='log'),
        dict(label='Log', xtype='log', ytype='log')
    ]

    buttons = []

    combs = _find_axes_combs(fig)

    for dataset in datasets:
        label = dataset.get('label')
        xtype = dataset.get('xtype')
        ytype = dataset.get('ytype')

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
