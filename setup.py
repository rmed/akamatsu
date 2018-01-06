# -*- coding: utf-8 -*-
#
# Akamatsu CMS
# https://github.com/rmed/akamatsu
#
# Copyright (C) 2018 Rafael Medina García <rafamedgar@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from setuptools import setup, find_packages

setup(
    name='akamatsu',
    version='1.0.0',

    description='Flask based CMS',
    long_description='',

    url='https://github.com/rmed/akamatsu',

    author='Rafael Medina García',
    author_email='rafamedgar@gmail.com',

    license='GPLv2+',

    classifiers=[],

    keywords='akamatsu cms flask web',

    packages=find_packages(),

    package_data={
        'akamatsu': [
            'migrations/*',
            'migrations/versions/*',
            'templates/*',
            'static/*'
        ]
    },
    exclude_package_data={
        '': ['static/gen/*']
    },

    zip_safe=False,
    entry_points={
        'console_scripts': [
            'akamatsu=akamatsu.commands:cli.main',
        ]
    }
)
