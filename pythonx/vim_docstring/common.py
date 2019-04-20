#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A series of commands for finding and getting different types of Vim folds.

Note:
    In Vim, the first line of a buffer's index is 1, not 0. There's a few
    points in this file where "1-based" is mentioned. That's what it means.

'''

# IMPORT STANDARD LIBRARIES
import ast
import re

# IMPORT THIRD-PARTY LIBRARIES
import vim


def is_fold_open(line):
    '''bool: If the given, 1-based line number is part of a closed fold.'''
    try:
        if vim.eval('foldlevel({line})'.format(line=line)) == '0':
            # There is no fold here. Therefore it cannot be open
            return False

        if vim.eval('foldclosed({line})'.format(line=line)) == '-1':
            # There is a fold at this line and it is open
            return True
    except Exception:
        return False

    return False


def get_current_buffer_root_node():
    '''tuple[`ast.Module`, list[str]]: Get the ast node and its lines.'''
    lines = list(vim.current.buffer)
    return (ast.parse("\n".join(lines)), lines)


def get_node_folds(root, lines):
    '''Find every fold in the given node.

    Args:
        root (`ast.Node`):
            The node which will be searched for child nodes which should have docstrings.
        lines (list[str]):
            The source-code lines that `root` represents.

    Returns:
        tuple[`ast.ClassDef` or `ast.FunctionDef` or `ast.Module`, int, int]:
            Every child node of `root` and the start row and end row of its
            docstring. The start and end rows are 1-based.

    '''
    folds = []

    for node in get_valid_nodes(root):
        first_child = node.body[0]
        if not isinstance(first_child, ast.Expr):
            continue

        end = first_child.lineno
        if '"""' in lines[end - 1]:
            bracket = '"""'
        elif "'''" in lines[end - 1]:
            bracket = "'''"
        else:
            continue

        if re.search(bracket + '.*' + bracket, lines[end - 1]):
            start = end
        else:
            start = node.lineno if hasattr(node, 'lineno') else 1
            for i, line in enumerate(lines[end-2 : start-1 : -1]):
                if bracket in line:
                    start = end - i - 1
                    break
            else:
                continue

        folds.append((node, start, end))

    return folds


def get_open_folds():
    '''tuple[`ast.Module`, list[`ast.Node`]]: Find every node that has a docstring which is folded.'''
    root, lines = get_current_buffer_root_node()

    folds = []
    for node, start, _ in get_node_folds(root, lines):
        if is_fold_open(start):
            folds.append(node)

    return (root, folds)


def get_parent_nodes(node):
    '''list[`ast.Node`]: Find every node that `node` is a part of.'''
    def _get_parent(node):
        try:
            return node.parent
        except AttributeError:
            return None

    parent = _get_parent(node)
    parents = []

    while parent:
        parents.append(parent)
        parent = _get_parent(parent)

    return parents


def get_valid_nodes(root):
    '''Find every node that would have a Python docstring.

    Args:
        root (`ast.Node`):
            The node which will be searched for child nodes which should have docstrings.

    Returns:
        list[`ast.ClassDef` or `ast.FunctionDef` or `ast.Module`]: The found nodes.

    '''
    nodes = []

    for node in ast.walk(root):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Module)):
            continue
        if not ast.get_docstring(node):
            continue

        nodes.append(node)

    return nodes


def attach_parents(root):
    '''Add a `parent` attribute to each child node in `root`.'''
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node
