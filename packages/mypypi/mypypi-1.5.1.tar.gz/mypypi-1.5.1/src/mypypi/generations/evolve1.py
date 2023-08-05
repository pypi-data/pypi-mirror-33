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

import os
import os.path
import time
import shutil

import logging

import zope.event
import zope.lifecycleevent
from zope.component import hooks
from zope.app.generations.utility import getRootFolder

import p01.fsfile.interfaces

import mypypi.storage
import mypypi.release
import mypypi.public
import mypypi.project


LOGGER = logging.getLogger('generation1')


def moveFSFile(oldPath, newPath, retry=0):
    """Move file to folder"""
    while retry <= 3:
        retry += 1
        try:
            shutil.move(oldPath, newPath)
        except Exception, e:
            LOGGER.error("ERROR: Can't move file from %s to %s" % (oldPath,
                newPath))
            LOGGER.exception(e)
            time.sleep(1)
            moveFSFile(oldPath, newPath, retry)
        # break while if everything is fine
        break


def fixFSFile(oldFSStorage, fsStorage, fsFile):
    # first fix fsID, remove full path and add relative path as fsID
    # ensure relative path
    if '\\' in fsFile.fsID:
        sep = '\\'
    elif '/' in fsFile.fsID:
        sep = '/'
    else:
        sep = None
    if sep is not None:
        fsFile.fsID = fsFile.fsID.split(sep)[-1]

    # get the old fsFile.path (note, we can't use the internals because the
    # IFSStorage is using the utility where we unregistered already)
    oldPath = os.path.join(oldFSStorage.getStorageDir(fsFile.fsNameSpace),
        fsFile.fsID)
    if not os.path.exists(oldPath):
        oPath = oldPath.replace('upload' + os.sep, '')
        if os.path.exists(oPath):
            oldPath = oPath
        else:
            oPath = oldPath.replace('mirror' + os.sep, '')
            if os.path.exists(oPath):
                oldPath = oPath
            else:
                oPath = oldPath.replace('distutils' + os.sep, '')
                if os.path.exists(oPath):
                    oldPath = oPath

    # remove fsNameSpace, BushyStorage doesn't use this
    fsFile.__dict__['fsNameSpace'] = None

    # get new fsID based on new bushy storage
    fsFile.fsID = fsStorage._getFSID(fsFile)
    # move file to new location in bushy storage
    newPath = fsFile.path
    LOGGER.warn("MOVE file from %s to %s" % (oldPath, fsFile.path))
    moveFSFile(oldPath, fsFile.path)


def evolve(context):
    """Evolve the ZODB.

    - use storage path given from runtime environment and adjust file path
      based on storage and namespace.

    """
    site = getRootFolder(context)

    LOGGER.warn("Start generation")

    # set the evolving site as the site
    originalSite = hooks.getSite()
    hooks.setSite(site)
    sm = site.getSiteManager()

    # get old storage and unregister
    oldFSStorage = sm['default']['FlatPathFSStorage']
    sm.unregisterUtility(oldFSStorage, p01.fsfile.interfaces.IFSStorage)

    # add and register new fsstorage
    fsStorage = mypypi.storage.FSStorage()
    fsStorage.fsFileFactory = mypypi.release.ReleaseFile
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(fsStorage))
    sm['default']['FSStorage'] = fsStorage
    # register new storage
    sm.registerUtility(fsStorage, p01.fsfile.interfaces.IFSStorage)

    # fix file path. Remove full storage path from fsID
    for pkg in site.values():
        for release in pkg.values():
            for fsFile in release.values():
                fixFSFile(oldFSStorage, fsStorage, fsFile)

    # adjust project file paths
    for folder in mypypi.public.getPublicContainer(site).values():
        for fsFile in folder.values():
            fixFSFile(oldFSStorage, fsStorage, fsFile)

    # adjust project file paths
    for project in mypypi.project.getProjectContainer(site).values():
        for fsFile in project.values():
            fixFSFile(oldFSStorage, fsStorage, fsFile)

    # move ghost files to new file system storage
    for key, obj in oldFSStorage._ghostFiles.items():
        fsStorage._ghostFiles.__setitem__(key, obj)

    # remove old storage
    del sm['default']['FlatPathFSStorage']

    # set original site back
    hooks.setSite(originalSite)
