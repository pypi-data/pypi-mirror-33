# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

from polarion_docstrings import checker


RESULTS = [
    (50, 0, u'P665 Missing "Polarion" section'),
    (54, 0, u'P665 Missing "Polarion" section'),
    (60, 4, u'P665 Missing "Polarion" section'),
    (10, 4, u'P665 Missing "Polarion" section'),
    (14, 8, u'P665 Missing "Polarion" section'),
    (21, 8, u'P669 Missing required field "initialEstimate"'),
    (23, 12, u'P667 Invalid value "nonexistent" of the "casecomponent" field'),
    (39,
     12,
     u'P668 Field "caselevel" should be handled by the "@pytest.mark.tier" marker'),
    (40,
     12,
     u'P668 Field "caseautomation" should be handled by the "@pytest.mark.manual" marker'),
    (41,
     12,
     u'P668 Field "linkedWorkItems" should be handled by the "@pytest.mark.requirements" marker'),
    (42, 12, u'P666 Unknown field "foo"')
]


def _strip_func(errors):
    return [(lineno, col, msg) for lineno, col, msg, __ in errors]


def test_checker(source_file):
    errors = checker.run_checks(None, source_file)
    errors = _strip_func(errors)
    assert len(errors) == len(RESULTS)
    assert errors == RESULTS
