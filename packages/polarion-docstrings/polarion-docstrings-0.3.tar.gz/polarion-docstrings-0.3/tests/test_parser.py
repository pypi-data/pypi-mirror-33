# encoding: utf-8
# pylint: disable=missing-docstring

from __future__ import unicode_literals

from polarion_docstrings import parser


RESULTS = [
    (50, 0, {}),
    (54, 0, {}),
    (60, 4, {}),
    (68,
     4,
     {u'assignee': (1, 8, u'mkourim'), u'initialEstimate': (2, 8, u'1/4')}),
    (10, 4, {}),
    (14, 8, {}),
    (21,
     8,
     {u'assignee': (1, 12, u'mkourim'),
      u'caseautomation': (19, 12, u'automated'),
      u'casecomponent': (2, 12, u'nonexistent'),
      u'caseimportance': (11, 12, u'low'),
      u'caselevel': (18, 12, u'level1'),
      u'expectedResults': [(8,
                            16,
                            u"1. Success outcome with really long description that doesn't "
                            u"fit into one line"),
                           (10, 16, u'2. second')],
      u'foo': (21, 12, u'this is an unknown field'),
      u'linkedWorkItems': (20, 12, u'FOO, BAR'),
      u'setup': (14, 12, u'Do this:\n- first thing\n- second thing'),
      u'teardown': (17, 12, u'Tear it down'),
      u'testSteps': [(4,
                      16,
                      u"1. Step with really long description that doesn't fit into one line"),
                     (6, 16, u'2. Do that')],
      u'title': (12,
                 12,
                 u"Some test with really long description that doesn't fit into one line")})
]


def test_parser(source_file):
    docstrings = parser.get_docstrings_in_file(None, source_file)
    assert len(docstrings) == len(RESULTS)
    assert docstrings == RESULTS
