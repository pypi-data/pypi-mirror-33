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
import doctest
import zipfile

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage

from zope.app.publication.zopepublication import ZopePublication
from zope.site.folder import rootFolder
from zope.app.testing import setup


class ContextStub(object):
    """Stub for the context argument passed to evolve scripts.

          from zope.app.zopeappgenerations import getRootFolder
          context = ContextStub()
          getRootFolder(context) is context.root_folder
        True

    """

    class ConnectionStub(object):
        def __init__(self, root_folder, db):
            self.root_folder = root_folder
            self.db = db

        def root(self):
            return {ZopePublication.root_name: self.root_folder}

        @property
        def _storage(self):
            try:
                return self.db._storage._base
            except AttributeError:
                #hmmm... ZODB got changes?
                return self.db._storage.base

        def get(self, oid):
            return self.db.open().get(oid)

    def __init__(self, rootFolder, db):
        self.root_folder = rootFolder
        self.connection = self.ConnectionStub(self.root_folder, db)


def getRootFolder(db):
    """Returns the Zope root folder."""
    connection = db.open()
    root = connection.root()
    return root[ZopePublication.root_name]


def unZipFile(filename):
    z = zipfile.ZipFile(filename)
    basepath = os.path.dirname(filename)
    for j in z.namelist():
        f = file(os.path.join(basepath, j),'wb')
        f.write(z.read(j))
        f.close()


def getDB(filename, package=None):
    """Returns a DB by it's path."""
    if package is not None:
        filename = doctest._module_relative_path(package, filename)
        package = package.__file__
    else:
        package = __file__
    filename = os.path.join(os.path.dirname(package), filename)
    zipfilename = filename+'.zip'

    if os.path.exists(filename):
        pass
    elif os.path.exists(zipfilename):
        unZipFile(zipfilename)
    else:
        raise ValueError("Fatal error, neither %s nor %s.zip found" %(
            filename, filename))

    fileStorage = FileStorage(filename)
    storage = DemoStorage("Demo Storage", fileStorage)
    return DB(storage)


def setUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site


def tearDown(test):
    setup.placefulTearDown()

###################
#sample usage of doSearch:

#def evolve(context):
#    """
#    """
#    storage = context.connection._storage
#
#    refmap = buildRefmap(storage) # can take a while
#
#    next_oid = None
#    n = 0
#    while True:
#        oid, tid, data, next_oid = storage.record_iternext(next_oid)
#
#        modname, classname = get_pickle_metadata(data)
#
#        if classname == "_LocalAdapterRegistry":
#            obj = context.connection.get(oid)
#            # Make sure that we tell all objects that they have been changed. Who
#            # cares whether it is true! :-)
#            obj._p_activate()
#            obj._p_changed = True
#            from pub.dbgpclient import brk; brk('192.168.32.1')
#
#            oid = obj._p_oid
#            path, additionals = doSearch(oid, refmap)
#
#            opath = [obj._p_jar[o] for o in path]
#
#            for o in opath:
#                try:
#                    print ox, ox.__name__
#                except:
#                    pass
#
#        if next_oid is None:
#            break
