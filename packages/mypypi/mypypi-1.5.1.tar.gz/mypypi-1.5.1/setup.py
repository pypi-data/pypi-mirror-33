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
"""Setup

$Id:$
"""

import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup (
    name='mypypi',
    version='1.5.1',
    author = "Projekt01 GmbH, 6330 Cham, Switzerland",
    author_email = "dev@projekt01.ch",
    description = "My Python Package Index (Standalone Server)",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('INSTALL.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "python buildout package index server egg pypi mirror private",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'https://pypi.org/pypi/mypypi',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = [],
    extras_require = dict(
        test = [
            'p01.checker',
            'p01.testbrowser',
            'p01.tester',
            'z3c.testing',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'BeautifulSoup',
        'docutils',
        'j01.form',
        'p01.accelerator',
        'p01.fsfile',
        'p01.fswidget',
        'p01.recipe.setup [paste]',
        'p01.remote',
        'p01.tmp',
        'p01.zmi',
        'requests',
        'z3c.authenticator',
        'z3c.breadcrumb',
        'z3c.configurator',
        'z3c.form',
        'z3c.formui',
        'z3c.indexer',
        'z3c.layer.ready2go',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.schema',
        'z3c.table',
        'z3c.tabular',
        'z3c.template',
        'zope.annotation',
        'zope.app.appsetup',
        'zope.app.component',
        'zope.app.generations',
        'zope.app.intid',
        'zope.app.publication',
        'zope.app.principalannotation',
        'zope.app.security',
        'zope.app.wsgi',
        'zope.app.authentication',
        'zope.app.broken',
        'zope.app.catalog',
        'zope.app.dependable',
        'zope.app.error',
        'zope.app.exception',
        'zope.app.folder',
        'zope.app.keyreference',
        'zope.app.principalannotation',
        'zope.app.securitypolicy',
        'zope.authentication',
        'zope.component',
        'zope.container',
        'zope.contentprovider',
        'zope.event',
        'zope.exceptions',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.principalannotation',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.securitypolicy',
        'zope.site',
        'zope.traversing',
        ],
    zip_safe = False,
    include_package_data = True,
    package_data = {'': ['*.txt', '*.cfg', '*.py', 'buildout.cfg'],},
    entry_points = """
        [paste.app_factory]
        main = mypypi.wsgi:application_factory
        """,
    )
