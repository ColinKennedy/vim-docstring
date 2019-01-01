#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The main module that is responsible for creating and opening folds.'''

# IMPORT THIRD-PARTY LIBRARIES
import logging
import vim

# IMPORT LOCAL LIBRARIES
from . import common


DEFAULT_VARIABLE = 'b:vim_docstring_open_folds'
LOGGER = logging.getLogger('vim_docstring')


def set_folds():
    '''Create folds for every Python docstring in the current buffer.'''
    root, lines = common.get_current_buffer_root_node()

    for _, start, end in common.get_node_folds(root, lines):
        vim.command("%d,%dfold" % (start, end))


def _get_unique_name(node):
    '''str: Get a special name for the given `ast.Node`.'''
    parents = common.get_parent_nodes(node)
    parent_names = [parent.name for parent in parents if hasattr(parent, 'name')]
    return ':'.join(parent_names + [node.name])


def save_opened_folds(variable=DEFAULT_VARIABLE):
    '''Save a list of every node with an open fold to the given Vim `variable`.'''
    root, nodes = common.get_open_folds()
    common.attach_parents(root)
    names = [_get_unique_name(node) for node in nodes]
    vim.command('let {variable} = {names!r}'.format(variable=variable, names=names))


def restore_opened_folds(variable=DEFAULT_VARIABLE):
    '''Find every saved, open Python docstring fold and open them.'''
    try:
        opened_folds = vim.eval(variable)
    except Exception:
        LOGGER.exception('Variable "{variable}" has no recorded, opened folds.'.format(variable=variable))
        return

    root, lines = common.get_current_buffer_root_node()
    common.attach_parents(root)

    for node, start, end in common.get_node_folds(root, lines):
        if _get_unique_name(node) in opened_folds and not common.is_fold_open(start):
            vim.command('{start},{end}foldopen'.format(start=start, end=end))
