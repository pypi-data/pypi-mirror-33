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
$Id: export.py 4599 2017-02-25 14:18:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import json
import cStringIO

import zope.interface
from zope.publisher.interfaces.http import IResult

from mypypi import interfaces


class ExportDataWrapper:
    """Export download wrapper"""

    zope.interface.implements(IResult)

    def __init__(self, f, chunksize=32768):
        self._file = f
        self.close = f.close
        self.chunksize = chunksize

    def __iter__(self):
        f = self._file
        while 1:
            v = f.read(self.chunksize)
            if v:
                yield v
            else:
                break


class ExportPage(object):
    """Export page"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data = {}
        for pkg in self.context.values():
            if interfaces.IMirrorPackage.providedBy(pkg):
                pkgType = 'MirrorPackage'
            else:
                pkgType = 'LocalPackage'
            for rel in pkg.values():
                if interfaces.IMirrorRelease.providedBy(rel):
                    relType = 'MirrorRelease'
                else:
                    relType = 'LocalRelease'
                fData = {}
                for f in rel.values():
                    fData[f.__name__] = {
                        '__name__': f.__name__,
                        'id': f.fsID,
                        'path': f.path,
                    }
                relData = {
                    '__name__': rel.__name__,
                    'typ': relType,
                    'files': fData,
                }
            data[pkg.__name__] = {
                'name': pkg.__name__,
                'typ': pkgType,
                'releases': relData,
            }
                    # {
                    # 'url': url,
                    # 'packagetype': f.packageType,
                    # 'filename': f.__name__,
                    # 'size': f.size,
                    # 'md5_digest': f.md5Digest,
                    # 'downloads': f.downloads,
                    # 'has_sig': f.hasSig,
                    # 'python_version': f.pythonVersion,
                    # 'comment_text': f.commentText,
                    # }


                    # {
                    # 'name': pkg.__name__,
                    # 'version': rel.__name__,
                    # 'stable_version': rel.stableVersion,
                    # 'author': rel.author,
                    # 'author_email': rel.authorEmail,
                    # 'maintainer': rel.maintainer,
                    # 'maintainer_email': rel.maintainerEmail,
                    # 'home_page': rel.homePage,
                    # 'license': rel.license,
                    # 'summary': rel.summary,
                    # 'description': rel.description,
                    # 'keywords': rel.keywords,
                    # 'platform': rel.platform,
                    # 'download_url': rel.downloadURL,
                    # 'classifiers': rel.classifiers,
                    # 'requires': rel.requires,
                    # # TODO: implement this
                    # 'requires_dist': [],
                    # 'provides': rel.provides,
                    # # TODO: implement this
                    # 'provides_dist': [],
                    # # TODO: implement this
                    # 'requires_external': [],
                    # # TODO: implement this
                    # 'requires_python': '',
                    # 'obsoletes': rel.obsoletes,
                    # # TODO: implement this
                    # 'obsoletes_dist': [],
                    # # TODO: implement this
                    # 'project_url': [],
                    # }

        sio = cStringIO.StringIO()
        sio.write(json.dumps(data))
        size = sio.tell()
        sio.seek(0)
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setHeader('Content-Disposition',
            'attachment; filename=export.json')
        self.request.response.setHeader('Content-Length', size)
        return ExportDataWrapper(sio)
