#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORT THIRD-PARTY LIBRARIES
import vim

# IMPORT LOCAL LIBRARIES
from . import common


DEFAULT_VARIABLE = 'b:vim_docstring_open_folds'


def set_folds():
    root, lines = common.get_current_buffer_root_node()

    for _, start, end in common.get_node_folds(root, lines):
        vim.command("%d,%dfold" % (start, end))


def save_opened_folds(variable=DEFAULT_VARIABLE):
    nodes = common.get_open_folds()
    names = [node.name for node in nodes]
    vim.command('let {variable} = {names!r}'.format(variable=variable, names=names))


def restore_opened_folds(variable=DEFAULT_VARIABLE):
    try:
        opened_folds = vim.eval(variable)
    except Exception:
        LOGGER.exception('Variable "{variable}" has no recorded, opened folds.'.format(variable=variable))
        return

    root, lines = common.get_current_buffer_root_node()
    for node, start, end in common.get_node_folds(root, lines):
        if node.name in opened_folds:
            vim.command('{start},{end}foldopen'.format(start=start, end=end))
