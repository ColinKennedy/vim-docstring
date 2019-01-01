#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''A series of commands for finding and getting different types of Vim folds.'''

# IMPORT STANDARD LIBRARIES
import ast
import re

# IMPORT THIRD-PARTY LIBRARIES
import vim


def is_fold_open(line):
    '''bool: If the given, 1-based line number is part of a closed fold.'''
    try:
        return vim.eval('foldclosed({line})'.format(line=line)) == '-1'
    except Exception:
        return False


def get_current_buffer_root_node():
    '''tuple[`ast.Node`, list[str]]: Get the module-level ast node and its lines.'''
    lines = list(vim.current.buffer)
    return (ast.parse("\n".join(lines)), lines)


def get_node_folds(root, lines):
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
    root, lines = get_current_buffer_root_node()

    folds = []
    for node, start, _ in get_node_folds(root, lines):
        if is_fold_open(start):
            folds.append(node)

    return folds


def get_valid_nodes(root):
    nodes = []

    for node in ast.walk(root):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            continue
        if not ast.get_docstring(node):
            continue

        nodes.append(node)

    return nodes
