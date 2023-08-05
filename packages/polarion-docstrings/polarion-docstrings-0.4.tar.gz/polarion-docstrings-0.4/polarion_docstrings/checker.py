# -*- coding: utf-8 -*-
"""
Checks Polarion docstrings.
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import sys

from setuptools_scm import get_version

from polarion_docstrings import parser
from polarion_docstrings import polarion_fields as pf


def _validate(docstring_dict, key):
    value = docstring_dict.get(key)
    if value is not None:
        return value[2] in pf.VALID_VALUES[key]
    return True


def _get_unknown_fields(docstring_dict):
    unknown = [(docstring_dict[key][0], docstring_dict[key][1], key) for key in docstring_dict
               if key not in pf.KNOWN_FIELDS]
    return unknown


def _get_invalid_fields(docstring_dict):
    results = {key: _validate(docstring_dict, key) for key in pf.VALID_VALUES}
    invalid = [
        (docstring_dict[key][0], docstring_dict[key][1], key) for key, result in results.items()
        if not result
    ]
    return invalid


def _get_missing_fields(docstring_dict):
    missing = [key for key in pf.REQUIRED_FIELDS if key not in docstring_dict]
    return missing


def _get_markers_fields(docstring_dict):
    markers = [(docstring_dict[key][0], docstring_dict[key][1], key) for key in pf.MARKERS_FIELDS
               if key in docstring_dict]
    return markers


def validate_docstring(docstring_dict):
    """Returns tuple with lists of problematic fields."""
    unknown = _get_unknown_fields(docstring_dict)
    invalid = _get_invalid_fields(docstring_dict)
    missing = _get_missing_fields(docstring_dict)
    markers = _get_markers_fields(docstring_dict)
    return unknown, invalid, missing, markers


def get_fields_errors(validated_docstring, docstring_dict, lineno=0, column=0):
    """Produces fields errors for the flake8 checker."""
    errors = []
    func = polarion_checks492
    unknown, invalid, missing, markers = validated_docstring

    for num, col, field in unknown:
        errors.append((lineno + num, col, 'P666 Unknown field "{}"'.format(field), func))
    for num, col, field in invalid:
        errors.append((lineno + num, col, 'P667 Invalid value "{}" of the "{}" field'.format(
            docstring_dict[field][2], field), func))
    for num, col, field in markers:
        errors.append((
            lineno + num,
            col,
            'P668 Field "{}" should be handled by the "@pytest.mark.{}" marker'.format(
                field, pf.MARKERS_FIELDS[field]),
            func
        ))
    for field in missing:
        errors.append(
            (lineno, column, 'P669 Missing required field "{}"'.format(field), func)
        )

    if errors:
        errors = sorted(errors, key=lambda tup: tup[0])
    return errors


def print_errors(errors):
    """Prints errors without using flake8."""
    for err in errors:
        print('line: {}:{}: {}'.format(err[0], err[1], err[2]), file=sys.stderr)


def check_docstrings(docstrings):
    """Runs checks on each docstring."""
    errors = []
    for lineno, column, doc_dict in docstrings:
        if doc_dict:
            valdoc = validate_docstring(doc_dict)
            errors.extend(get_fields_errors(valdoc, doc_dict, lineno, column))
        else:
            errors.append((lineno, column, 'P665 Missing "Polarion" section', polarion_checks492))
    return errors


def run_checks(tree, filename):
    """Checks docstrings in python source file."""
    docstrings = parser.get_docstrings_in_file(tree, filename)
    errors = check_docstrings(docstrings)
    return errors


def polarion_checks492(tree, filename):
    """The flake8 entry point."""
    abs_filename = os.path.abspath(filename)
    __, tail = os.path.split(abs_filename)
    # check only test files under cfme/tests
    if '/cfme/tests/' not in abs_filename or tail.find('test_') != 0:
        return []  # must be iterable
    return run_checks(tree, filename)


polarion_checks492.name = 'polarion_checks'
polarion_checks492.version = get_version(root='..', relative_to=__file__)
