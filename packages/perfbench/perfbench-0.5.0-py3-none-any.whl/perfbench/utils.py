#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
from IPython import get_ipython


def is_interactive():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def create_empty_array_of_shape(shape):
    if shape:
        return [create_empty_array_of_shape(shape[1:]) for _ in range(shape[0])]


def cmd_exists(cmd):
    return shutil.which(cmd) is not None
