#!/usr/bin/env python
#
# Copyright (C) 2017 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
# pylint: disable=bad-whitespace

from setuptools import setup

# Grab description for Pypi
with open('README.md') as fhl:
    DESC = fhl.read()

setup(
    name             = "django-boxed-alerts",
    version          = "1.1",
    description      = "Robust user emailing and notification system for django web framework.",
    long_description = DESC,
    author           = 'Martin Owens',
    url              = 'https://gitlab.com/doctormo/django-boxed-alerts',
    author_email     = 'doctormo@gmail.com',
    platforms        = 'linux',
    license          = 'AGPLv3',
    packages         = ['alerts'],
    install_requires = ['django>=1.11,<2.0',],
    classifiers      = [
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
