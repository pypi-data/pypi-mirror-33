##############################################################################
#
# Copyright (c) 2018 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Tests
$Id: package.py 4865 2018-05-16 14:06:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

from z3c.testing import InterfaceBaseTest

from mypypi import interfaces
from mypypi import package


class LocalPackageTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ILocalPackage

    def getTestClass(self):
        return package.LocalPackage


class MirrorPackageTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMirrorPackage

    def getTestClass(self):
        return package.MirrorPackage

    def getTestPos(self):
        return ('http://pypy.python.org/pypi',)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LocalPackageTest),
        unittest.makeSuite(MirrorPackageTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
