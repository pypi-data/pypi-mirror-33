# -*- coding: utf-8 -*-
"""
Parses Polarion docstring.
"""

from __future__ import absolute_import, unicode_literals

import ast


FORMATED_KEYS = ('setup', 'teardown')


# pylint: disable=too-few-public-methods
class SECTIONS(object):
    """Valid sections in Polarion docstring."""
    polarion = 'Polarion'
    steps = 'testSteps'
    results = 'expectedResults'


def _get_section_start(doc_list, section):
    """Finds the line with "section" (e.g. "Polarion", "testSteps", etc.)."""
    section = '{}:'.format(section)
    for index, line in enumerate(doc_list):
        if section != line.strip():
            continue
        indent = len(line) - len(line.lstrip(' '))
        return index + 1, indent
    return None, None


def _get_key_value(line):
    """Gets the key and value out of docstring line."""
    data = line.split(':')
    if len(data) == 1:
        data.append('')

    key = data[0].strip()

    value = ':'.join(data[1:]).strip()
    if value == 'None':
        value = None

    return key, value


# pylint: disable=too-many-locals
def _lines_to_dict(lines, start=0, lineno_offset=0, stop=None):
    """Creates dictionary out of docstring lines.

    Includes column and line number info for each record.
    """
    if stop:
        lines = lines[start:stop]
    else:
        lines = lines[start:]

    lines_dict = {}
    indent = len(lines[0]) - len(lines[0].lstrip(' '))
    prev_key = None
    for num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped:
            break

        curr_indent = len(line) - len(line.lstrip(' '))

        if curr_indent < indent:
            break

        # check if the line should be appended to previous key
        first_word = line_stripped.split(' ')[0] or line_stripped
        if prev_key and curr_indent > indent and first_word[-1] != ':':
            sep = '\n' if prev_key in FORMATED_KEYS else ' '
            prev_lineno, prev_indent, prev_value = lines_dict[prev_key]
            lines_dict[prev_key] = (
                prev_lineno, prev_indent, '{}{}{}'.format(prev_value, sep, line_stripped))
            continue
        else:
            prev_key = None

        if curr_indent > indent:
            continue

        key, value = _get_key_value(line)
        lines_dict[key] = num + lineno_offset, indent, value
        prev_key = key

    return lines_dict


def _lines_to_list(lines, start=0, lineno_offset=0, stop=None):
    """Creates list out of docstring lines.

    Includes column and line number info for each line.
    """
    if stop:
        lines = lines[start:stop]
    else:
        lines = lines[start:]

    lines_list = []
    indent = len(lines[0]) - len(lines[0].lstrip(' '))
    for num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        curr_indent = len(line) - len(line.lstrip(' '))
        if curr_indent < indent:
            break

        # check if the line should be appended to previous key
        first_word = line_stripped.split(' ')[0] or line_stripped
        if curr_indent > indent and first_word[-1] != ':':
            prev_lineno, prev_indent, prev_value = lines_list.pop()
            lines_list.append(
                (prev_lineno, prev_indent, '{} {}'.format(prev_value, line_stripped)))
            continue

        if curr_indent > indent:
            continue
        lines_list.append((num + lineno_offset, indent, line_stripped))

    return lines_list


def parse_docstring(docstring):
    """Parses docstrings to dictionary. E.g.:

    Polarion:
        assignee: mkourim
        casecomponent: nonexistent
        testSteps:
            1. Step with really long description
               that doesn't fit into one line
            2. Do that
        expectedResults:
            1. Success outcome with really long description
               that doesn't fit into one line
            2. 2
        caseimportance: low
        title: Some test with really long description
               that doesn't fit into one line
        setup: Do this:
               - first thing
               - second thing
        foo: this is an unknown field

    This is not included.
    """
    doc_list = docstring.split('\n')

    polarion_start, __ = _get_section_start(doc_list, SECTIONS.polarion)
    if not polarion_start:
        return None

    docstring_dict = _lines_to_dict(doc_list, start=polarion_start)
    if SECTIONS.steps in docstring_dict and docstring_dict[SECTIONS.steps][2]:
        steps_start, __ = _get_section_start(doc_list, SECTIONS.steps)
        steps_list = _lines_to_list(
            doc_list, start=steps_start, lineno_offset=steps_start - polarion_start)
        docstring_dict[SECTIONS.steps] = steps_list
    if SECTIONS.results in docstring_dict and docstring_dict[SECTIONS.results][2]:
        results_start, __ = _get_section_start(doc_list, SECTIONS.results)
        results_list = _lines_to_list(
            doc_list, start=results_start, lineno_offset=results_start - polarion_start)
        docstring_dict[SECTIONS.results] = results_list

    return docstring_dict


def _get_tree(filename):
    with open(filename) as infile:
        source = infile.read()

    tree = ast.parse(source, filename=filename)
    return tree


def get_docstring_from_func(func_node):
    """Gets docstring from function definition."""
    docstring = None
    try:
        if (func_node.body and
                isinstance(func_node.body[0], ast.Expr) and
                isinstance(func_node.body[0].value, ast.Str)):
            docstring = func_node.body[0].value.s
    # pylint: disable=broad-except
    except Exception:
        return None

    # for Python2
    try:
        docstring = docstring.decode('utf-8')
    except AttributeError:
        pass

    return docstring


def get_docstrings_in_file(tree, filename, tests_only=True):
    """Returns parsed Polarion docstrings present in the python source file."""
    if not tree:
        tree = _get_tree(filename)

    docstrings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        if tests_only and node.name.find('test_') != 0:
            continue

        docstring = get_docstring_from_func(node)

        # test doesn't have docstring, i.e. it's missing also the Polarion section
        if not docstring:
            docstrings.append((node.body[0].lineno - 1, node.col_offset, {}))
            continue

        doc_list = docstring.split('\n')
        docstring_start = node.body[0].lineno - len(doc_list)
        polarion_start, polarion_column = _get_section_start(doc_list, SECTIONS.polarion)

        if not polarion_start:
            # docstring is missing the Polarion section
            docstrings.append((docstring_start + 1, node.col_offset + 4, {}))
            continue

        polarion_offset = docstring_start + polarion_start
        docstrings.append((polarion_offset, polarion_column, parse_docstring(docstring)))

    return docstrings
