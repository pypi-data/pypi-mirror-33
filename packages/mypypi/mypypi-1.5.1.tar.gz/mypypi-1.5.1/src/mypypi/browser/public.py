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
$Id: public.py 4599 2017-02-25 14:18:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL

import z3c.pagelet.browser

import p01.fsfile.browser


class PublicLinks(z3c.pagelet.browser.BrowserPagelet):
    """Public file management page."""

    @property
    def links(self):
        baseURL = absoluteURL(self.context, self.request)
        return [{'name':name,
                  'url': '%s/%s' % (baseURL, name),
                  #'date': self.getCreatedDate(fle),
                  }
                for name, fle in self.context.items()]


class PublicFileDownload(p01.fsfile.browser.FSFileDownload):
    """Public file download."""

    def __call__(self):
        return super(PublicFileDownload, self).__call__()
