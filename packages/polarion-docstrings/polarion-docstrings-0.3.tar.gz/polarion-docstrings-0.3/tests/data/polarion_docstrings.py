# encoding: utf-8
# pylint: disable=missing-docstring,no-self-use

from __future__ import unicode_literals

import pytest


class TestClassFoo(object):
    def test_in_class_no_docstring(self):
        pass

    def test_in_class_no_polarion(self):
        """FOO"""
        pass

    @pytest.mark.skip
    def test_in_class_polarion(self):
        """FOO

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
                2. second
            caseimportance: low
            title: Some test with really long description
                   that doesn't fit into one line
            setup: Do this:
                   - first thing
                   - second thing
            teardown: Tear it down
            caselevel: level1
            caseautomation: automated
            linkedWorkItems: FOO, BAR
            foo: this is an unknown field

        This is not included.
        """
        pass


@pytest.mark.skip
def test_annotated_no_docstring():
    pass


def test_standalone_no_docstring():
    pass


@pytest.mark.skip
def test_annotated_no_polarion():
    """FOO"""
    pass


@pytest.mark.skip
def test_annotated_polarion():
    """FOO

    Polarion:
        assignee: mkourim
        initialEstimate: 1/4
    """
    pass
