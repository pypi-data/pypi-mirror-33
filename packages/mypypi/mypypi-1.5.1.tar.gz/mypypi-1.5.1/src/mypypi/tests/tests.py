##############################################################################
#
# Copyright (c) 2018 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Tests
$Id: tests.py 4865 2018-05-16 14:06:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import re
import unittest
import doctest

import mypypi.testing


def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite('source.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('README.txt',
            setUp=mypypi.testing.placefulSetUp,
            tearDown=mypypi.testing.placefulTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
