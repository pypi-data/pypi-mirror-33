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

import unittest

import mypypi.testing


def test_suite():
    suite = unittest.TestSuite((
        mypypi.testing.FunctionalDocFileSuite('setuptools.txt'),
        mypypi.testing.FunctionalDocFileSuite('mirror.txt'),
        mypypi.testing.FunctionalDocFileSuite('keasbuild.txt'),
        ))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')