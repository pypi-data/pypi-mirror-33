##############################################################################
#
# Copyright (c) 2018 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Tests
$Id: site.py 4865 2018-05-16 14:06:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

from z3c.testing import InterfaceBaseTest

from mypypi import interfaces
from mypypi import site


class SiteTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IPYPISite

    def getTestClass(self):
        return site.PYPISite


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SiteTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
