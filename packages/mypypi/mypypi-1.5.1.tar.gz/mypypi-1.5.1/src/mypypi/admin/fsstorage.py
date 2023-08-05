##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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

from zope.security.proxy import removeSecurityProxy

import z3c.pagelet.browser

from p01.fsfile.storage import getFSStoragePath


class FSStorage(z3c.pagelet.browser.BrowserPagelet):
    """FSStorage"""

    def getFSStorage(self):
        sm = removeSecurityProxy(self.context).getSiteManager()
        return sm['default']['FSStorage']

    @property
    def fsStoragePath(self):
        fsStorage = self.getFSStorage()
        return fsStorage.path

    @property
    def msg(self):
        return (
            u"The release files are stored on the local file system using the "
            u"directory <strong>%s</strong> as it's base path." %
            self.fsStoragePath)
