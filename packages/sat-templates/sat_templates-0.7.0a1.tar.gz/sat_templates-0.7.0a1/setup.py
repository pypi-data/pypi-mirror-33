#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT templates: collection of templates
# Copyright (C) 2017  Xavier Maillard (xavier@maillard.im)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from setuptools import setup

base = None
NAME = 'sat_templates'
is_wheel = 'bdist_wheel' in sys.argv

# https://stackoverflow.com/a/36693250

def get_package_data(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


with open(os.path.join(NAME, 'VERSION')) as f:
    VERSION = f.read().strip()
is_dev_version = VERSION.endswith('D')


def sat_templates_dev_version():
    """Use mercurial data to compute version"""
    def version_scheme(version):
        return VERSION.replace('D', '.dev0')

    def local_scheme(version):
        return "+{rev}.{distance}".format(
            rev=version.node[1:],
            distance=version.distance)

    return {'version_scheme': version_scheme,
            'local_scheme': local_scheme}


setup_info = dict(
    name=NAME,
    version=VERSION,
    description=u'Templates for Salut à Toi XMPP client',
    long_description=u'SàT Template is a common module which can be used by any SàT '
                     u'frontend to generate documents (mostly HTML but not only).',
    author='Association « Salut à Toi »',
    author_email='contact@salut-a-toi.org',
    url='https://salut-a-toi.org',
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 2 :: Only',
                 'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
                 ],
    install_requires=[],
    setup_requires=['setuptools_scm'] if is_dev_version else [],
    use_scm_version=sat_templates_dev_version if is_dev_version else False,
    packages=['sat_templates'],
    package_data={'sat_templates': get_package_data('sat_templates') },
    zip_safe=True,
)

setup(**setup_info)
