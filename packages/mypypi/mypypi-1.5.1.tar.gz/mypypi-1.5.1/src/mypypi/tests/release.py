##############################################################################
#
# Copyright (c) 2018 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Tests
$Id: release.py 4865 2018-05-16 14:06:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

from z3c.testing import InterfaceBaseTest

from mypypi import interfaces
from mypypi import release


class LocalReleaseTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ILocalRelease

    def getTestClass(self):
        return release.LocalRelease


class MirrorReleaseTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMirrorRelease

    def getTestClass(self):
        return release.MirrorRelease


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LocalReleaseTest),
        unittest.makeSuite(MirrorReleaseTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
