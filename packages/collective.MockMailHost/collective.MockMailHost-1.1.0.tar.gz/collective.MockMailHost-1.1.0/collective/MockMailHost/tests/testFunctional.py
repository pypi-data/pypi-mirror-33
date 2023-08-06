# -*- coding: utf-8 -*-
from collective.MockMailHost.testing import COLLECTIVE_MOCKMAILHOST_FUNCTIONAL_TESTING
from collective.MockMailHost.testing import optionflags
from plone.testing import layered

import doctest
import unittest


doctests = (
    'SendEmail.txt',
)

def test_suite():
    suite = unittest.TestSuite()
    tests = [
        layered(
            doctest.DocFileSuite(
                'tests/{0}'.format(test_file),
                package='collective.MockMailHost',
                optionflags=optionflags,
            ),
            layer=COLLECTIVE_MOCKMAILHOST_FUNCTIONAL_TESTING,
        )
        for test_file in doctests
    ]
    suite.addTests(tests)
    return suite
