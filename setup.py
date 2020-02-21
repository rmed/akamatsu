# -*- coding: utf-8 -*-
#
# Akamatsu CMS
# https://github.com/rmed/akamatsu
#
# MIT License
#
# Copyright (c) 2020 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup, find_packages

setup(
    name='akamatsu',
    version='2.0.0',

    description='Flask based CMS',
    long_description='',

    url='https://github.com/rmed/akamatsu',

    author='Rafael Medina García',
    author_email='rafamedgar@gmail.com',

    license='MIT',
    classifiers=[],
    keywords='akamatsu cms flask web',

    packages=find_packages(),

    include_package_data=True,
    exclude_package_data={
        '': ['static/.webassets-cache/*']
    },

    zip_safe=False,

    install_requires=[
        'awesome-slugify==1.6.5',
        'bcrypt>=3.1.7',
        'blinker==1.4',
        'Flask==1.1.1',
        'Flask-Analytics==0.6.0',
        'Flask-Assets==2.0',
        'Flask-Babel==1.0.0',
        'Flask-Discussion==0.1.0',
        'Flask-Login==0.5.0',
        'Flask-Migrate==2.5.2',
        'Flask-Mail==0.9.1',
        'Flask-Misaka==1.0.0',
        'Flask-SQLAlchemy==2.4.1',
        'Flask-WTF==0.14.3',
        'hashids==1.2.0',
        'passlib>=1.7.2',
        'Pygments>=2.5.2',
        'Werkzeug>=1.0.0'
    ],

    extras_require={
        'dev': [
            'cssmin==0.2.0',
            'Flask-DebugToolbar==0.11.0',
            'libsass==0.19.4'
        ]
    },

    entry_points={
        'console_scripts': [
            'akamatsu=akamatsu.commands:cli.main',
        ]
    }
)
