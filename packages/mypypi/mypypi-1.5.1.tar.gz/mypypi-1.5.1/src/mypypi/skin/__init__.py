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

import zope.browserresource.file
import zope.contentprovider.interfaces
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL
from zope.component import hooks
from zope.app.security.interfaces import IUnauthenticatedPrincipal

import mypypi.api
import mypypi.layer


class IPYPIBrowserSkin(mypypi.layer.IPYPIBrowserLayer):
    """The ``PYPI`` browser skin."""


class SiteURL(BrowserPage):

    def __call__(self):
        return absoluteURL(hooks.getSite(), self.request)


class SiteTitle(BrowserPage):

    def __call__(self):
        site = hooks.getSite()
        if site is not None:
            return site.title
        return u''


class ISAuthenticated(BrowserPage):

    def __call__(self):
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)


class CanView(BrowserPage):

    def __call__(self):
        return mypypi.api.checkViewPermission(self.context)


class CanManagePackages(BrowserPage):

    def __call__(self):
        return mypypi.api.checkManagePackagesPermission(self.context)



class Favicon(zope.browserresource.file.FileResource):
    """Favicon provider for IHTTPRequest

    ATTENTION: this is a view registered for * and is used at site level.
    The favicon.ico is registered as a simple resource (non cdn) and get
    delivered without the cdn concept. The FileResource provides caching, this
    means we don't worry if this icon doesn't get delivered from the cdn
    webserver.

    NOTE: this page will use the correct ico via layers. This means there is
    no need to register another favicon.icon page.

    """

    def chooseContext(self):
        resource = zope.component.queryAdapter(self.request, name='favicon.ico')
        return resource.context


class IHeaderProvider(zope.contentprovider.interfaces.IContentProvider):
    """Header provider."""

