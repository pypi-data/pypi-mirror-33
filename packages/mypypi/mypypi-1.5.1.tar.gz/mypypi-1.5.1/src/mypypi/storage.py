##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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

import os.path
import sys

import BTrees.OOBTree
from zope.app.appsetup.product import getProductConfiguration

import p01.fsfile.storage
from p01.fsfile.storage import getFSStoragePath
from p01.fsfile.storage import BushyFSStorageBase
from p01.tmp import exceptions
from p01.tmp import storage


def getTMPStoragePath(confKey='storage', key='P01_TMP_STORAGE_PATH'):
    path = None
    config = getProductConfiguration('p01.tmp')
    if config is not None:
        path = config.get(confKey)
    else:
        path = os.environ.get(key)
    # tweak windows path
    if path is None:
        raise ValueError(
            "You must define p01.tmp 'storage' for run this server "
            "or remove the p01/tmp/default.zcml from your configuration.zcml. "
            "See p01/tmp/wsgi.py how you can define this env variable.")
    if sys.platform == 'win32':
        # fix buildout based path setup like we do in buildout.cfg
        # ${buildout:directory}/parts/tmp
        parts = path.split('/')
        path = os.path.join(*parts)
    if not os.path.exists(path):
        raise exceptions.MissingStoragePathError(
            "Given tmp storage path '%s' does not exist" % path)
    return unicode(path)

tmpPath = getTMPStoragePath()
tmpStorage = storage.TMPStorage(tmpPath)


class FSStorage(p01.fsfile.storage.BushyFSStorage):
    """Bushy storage using a relativ path"""

    def __init__(self):
        self._ghostFiles = BTrees.OOBTree.OOBTree()
        # setup path
        if not os.path.exists(self.path):
            # ensure path
            os.mkdir(self.path, 0700)

    # def addFSFile(self, fsFile):
    #     """Add existing FSFile to this storage

    #     Note: this method is used for migration.
    #     """
    #     fsFile.path

    @property
    def path(self):
        # adhoc relativ path lookup
        path = p01.fsfile.storage.getFSStoragePath(product='p01.fsfile',
            confKey='storage', envKey='P01_FSSTORAGE_PATH')
        return unicode(path)
