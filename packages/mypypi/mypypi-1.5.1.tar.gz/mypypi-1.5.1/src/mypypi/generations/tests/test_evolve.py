##############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
import doctest

from zope.dottedname import resolve

from mypypi.generations import testing

#path to doctest, a module if the db depends on it
docTestPaths = (
    ('../evolve1.txt', ''),
)


def test_suite():
    suites = []
    for filename, module in docTestPaths:
        works = True

        if module:
            #try to load it
            try:
                resolve.resolve(module)
            except ImportError:
                works = False
            except AttributeError:
                works = False

        if works:
            suites.append(doctest.DocFileSuite(
                filename,
                setUp=testing.setUp, tearDown=testing.tearDown,
                globs={
                    'getRootFolder': testing.getRootFolder,
                    'getDB': testing.getDB,
                    },
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ))
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
