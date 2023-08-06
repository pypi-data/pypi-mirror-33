#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT tmp: repository to store temporary patches for third party software
# Copyright (C) 2017  Arnaud Joset (info@agayon.be)
# Copyright (C) 2009-2017  Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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
from setuptools import setup


NAME = 'sat_tmp'


setup(
    name=NAME,
    version='0.7.0a2',
    description=u'Salut à Toi temporary third party patches',
    long_description=(u'This module is used by Salut à Toi project to patch third party '
                      u'modules when the patches are not yet available upstream. Patches '
                      u'are removed from this module once merged upstream.'),
    author='Association « Salut à Toi »',
    author_email='contact@salut-a-toi.org',
    url='https://salut-a-toi.org',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
                 'Operating System :: POSIX :: Linux',
                 'Topic :: Communications :: Chat'],
    install_requires=['wokkel >= 0.7.1'],
    packages=['sat_tmp', 'sat_tmp.wokkel', 'sat_tmp.wokkel.test'],
    data_files=[(os.path.join('share/doc', NAME),
                ['README', 'COPYING'])],
)
