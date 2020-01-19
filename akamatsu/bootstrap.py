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

"""This file contains miscelaneous bootstrapping code."""

import os

from flask_babel import lazy_gettext as _l



# Static configuration values
BASE_CONFIG = {
    # Localization
    'BABEL_DEFAULT_LOCALE': 'en',
    'BABEL_DEFAULT_TIMEZONE': 'UTC',

    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,

    # Flask-Login
    'SESSION_PROTECTION': 'strong',

    # Passlib
    'PASSLIB_SCHEMES': ['bcrypt'],
    'PASSLIB_ALG_BCRYPT_ROUNDS': 14,

    'PAGE_ITEMS': 10,
    'LOCALE': 'en',
    'TIMEZONE': 'UTC'
}


# Development defaults applied on top of BASE_CONFIG if no configuration
# is specified
DEV_CONFIG = {
    'SECRET_KEY': 'potato',
    'DEBUG': True,
    'TESTING': True,

    # Database path
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////{}'.format(os.path.join(os.getcwd(), "testdb.sqlite")),

    # Debug toolbar
    'DEBUG_TB_INTERCEPT_REDIRECTS': False,

    # Site name
    'SITENAME': 'akamatsu',

    # Site language
    'LOCALE': 'en',

    # Items per page in pagination
    'PAGE_ITEMS': 1,

    # Hashids
    'HASHIDS_SALT': 'hashedpotatoes',
    # Minimum length
    'HASHIDS_LENGTH': 8,

    # Flask-Mail
    'MAIL_SERVER': 'localhost',
    'MAIL_PORT': 25,
    'MAIL_USE_SSL': False,
    'MAIL_USE_TLS': False,
    'MAIL_DEFAULT_SENDER': '',
    'MAIL_USERNAME': '',
    'MAIL_PASSWORD': '',

    # Celery
    'USE_CELERY': False,
    'CELERY_BROKER_URL': 'redis://localhost:6379/1',
    'CELERY_RESULT_BACKEND': 'redis://localhost:6379/1',

    # Social links
    'SOCIAL': [
        {
            'link': 'https://github.com/rmed/akamatsu',
            'glyph': 'fab fa-github'
        },
    ],

    # Navigation bar
    'NAVBAR': [
        {
            'link': '/',
            'text': 'Home'
        },
        {
            'link': '/blog',
            'text': 'Blog'
        },
    ],

    # Footer
    'FOOTER_LEFT': 'Left footer',
    'FOOTER_RIGHT': 'Right footer'
}
