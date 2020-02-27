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

"""This file contains utility code."""

from functools import wraps
from urllib.parse import urlparse, urljoin

import misaka
import pytz

from flask import current_app, flash, redirect, request, url_for
from flask_babel import _
from flask_login import current_user
from flask_mail import Message
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class CeleryWrapper(object):
    """Wrapper for deferred initialization of Celery.

    The wrapper expects the following configuration parameters:

    - `CELERY_RESULT_BACKEND`: URL to the backend used for obtaining results.
    - `CELERY_BROKER_URL`: URL to the broker.
    """

    def __init__(self):
        self._celery = None
        self.task = None

    def __getattr__(self, attr):
        """Wrap internal celery attributes."""
        if attr == 'init_app':
            return getattr(self, attr)

        return getattr(self._celery, attr)

    def init_app(self, app):
        """Create a celery instance for the application.

        Args:
            app: Application instance.

        Raises:
            `KeyError` in case a configuration parameter is missing.
        """
        # Celery is optional, import it here rather than globally
        from celery import Celery

        celery_instance = Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL']
        )

        celery_instance.conf.update(app.config)
        TaskBase = celery_instance.Task

        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        celery_instance.Task = ContextTask

        self._celery = celery_instance
        self.task = self._celery.task


class CryptoManager(object):
    """Wrapper for passlib cryptography.

    The manager expects the following configuration variables:

    - `PASSLIB_SCHEMES`: List of passlib hashes for the underlying
        `CryptoContext` object. If a string is provided, it should be a
        comma-separated list of hashes supported by `passlib`. Defaults to
        `'bcrypt'`.
    - `PASSLIB_DEPRECATED`: List of passlib hashes that are deprecated
        (defaults to `"auto"`, which will deprecate all hashes except
        for the first hash type present in the `PASSLIB_SCHEMES` configuration
        variable). If a string different from `"auto"` is provided, it should
        be a comma-separated list of hashes supported by `passlib`. Defaults
        to an empty list.

    Moreover, the manager offers a direct translation of optional algorithm options for
    the underlying context (see
    <https://passlib.readthedocs.io/en/stable/lib/passlib.context.html#algorithm-options>).
    These are in the form `PASSLIB_ALG_<SCHEME>_<CONFIG>` and will be translated to the
    appropriate `<scheme>__<config>` configuration variable name internally.
    """

    def __init__(self):
        self._context = None

    def __getattr__(self, attr):
        """Wrap the internal passlib context."""
        if attr in ('init_app', '_context'):
            return getattr(self, attr)

        # Calling hasher methods
        return getattr(self._context, attr)

    def init_app(self, app):
        """Initialize manager.

        Args:
            app: Application instance

        Raises:
            `ModuleNotFoundError` in case `passlib` is not installed or
            `KeyError` if a configuration variable is missing.
        """
        from passlib.context import CryptContext

        schemes = app.config.get('PASSLIB_SCHEMES', 'bcrypt')
        deprecated = app.config.get('PASSLIB_DEPRECATED', 'auto')

        if isinstance(schemes, str):
            schemes = [s.strip() for s in schemes.split(',')]

        if isinstance(deprecated, str):
            deprecated = [d.strip() for d in deprecated.split(',')]

        params = {
            'schemes': schemes,
            'deprecated': deprecated,
        }

        # Set algorithm options
        for key in [k for k in app.config if k.startswith('PASSLIB_ALG_')]:
            value = app.config[key]
            scheme, option = key.replace('PASSLIB_ALG_', '').lower().split('_', 1)

            params['{}__{}'.format(scheme, option)] = value

        self._context = CryptContext(**params)


class HashidsWrapper(object):
    """Wrapper for deferred initialization of Hashids.

    This is optional and can be disabled by setting the configuration
    parameter `USE_HASHIDS` to `False`.

    If used, the wrapper expects the following configuration parameters:

    - `HASHIDS_SALT`: Salt to use when hashing IDs.
    - `HASHIDS_LENGTH`: Minimum length of the hash (defaults to 8).
    """

    def __init__(self):
        self._hasher = None

    def __getattr__(self, attr):
        """Wrap internal Hashids attributes."""
        if attr in ('init_app', '_hasher', '_initialized'):
            return getattr(self, attr)

        # Calling hasher methods
        return getattr(self._hasher, attr)

    def init_app(self, app):
        """Create a Hashids instance for the application.

        Args:
            app: Application instance

        Raises:
            `ModuleNotFoundError` in case `hashids` is not installed or
            `KeyError` if a configuration variable is missing.
        """
        from hashids import Hashids

        self._hasher = Hashids(
            salt=app.config['HASHIDS_SALT'],
            min_length=app.config.get('HASHIDS_LENGTH', 8)
        )


class HighlighterRenderer(misaka.HtmlRenderer):
    """Custom renderer to use with Misaka and pygments."""

    def blockcode(self, text, lang):
        if not lang:
            return '\n<pre><code>{}</code></pre>\n'.format(text.strip())

        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()

        return highlight(code=text, lexer=lexer, formatter=formatter)


def allowed_roles(*roles):
    """Decorator to allow only specific roles to access the route.

    This also checks whether the user is logged in.
    """
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            # Check user is logged in
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()

            # Check roles
            if set(roles).isdisjoint(current_user.role_names):
                flash(
                    _('You do not have permission to access the page'),
                    'warning'
                )
                return redirect(url_for('admin.home'))

            return f(*args, **kwargs)
        return decorator
    return wrapper


def datetime_to_utc(original):
    """Converts a datetime object to UTC

    This is done by taking into account the timezone configured in the
    application. If no valid timezone is specified, defaults to UTC.

    Args:
        value (datetime): Datetime object to convert.

    Returns:
        Converted datetime object.
    """
    app_tz = current_app.config.get('TIMEZONE', 'UTC')

    if not app_tz in pytz.common_timezones:
        app_tz = 'UTC'

    tz = pytz.timezone(app_tz)

    local = tz.localize(original)
    utc_dt = local.astimezone(pytz.utc)

    return utc_dt


def utc_to_local_tz(original):
    """Converts a UTC datetime object to application timezone.

    This is done by taking into account the timezone configured in the
    application. If no valid timezone is specified, defaults to UTC.

    Args:
        value (datetime): Datetime object to convert.

    Returns:
        Converted datetime object.
    """
    app_tz = current_app.config.get('TIMEZONE', 'UTC')

    if not app_tz in pytz.common_timezones:
        app_tz = 'UTC'

    utc = pytz.utc.localize(original)
    local = utc.astimezone(pytz.timezone(app_tz))

    return local


def is_allowed_file(filename):
    """Check if a file extension is allowed.

    Args:
        filename (str): Name of the file to check.

    Returns:
        True if the file upload is allowed.
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


def is_safe_url(target):
    """Check whether the target is safe for redirection.

    Args:
        target (str): Target URL/path.

    Returns:
        `True` if the URL is safe, otherwise `False`.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def send_email(*args, **kwargs):
    """Send an email.

    Emails are sent asynchronously if Celery is enabled.

    All arguments are passed as-is to Flask-Mail.

    Returns:
        Mail send result or `None`.
    """
    from akamatsu import mail

    if current_app.config.get('USE_CELERY', False):
        from akamatsu.async_tasks import async_mail

        async_mail.delay(*args, **kwargs)

    else:
        message = Message(*args, **kwargs)

        return mail.send(message)


def is_ajax():
    """Detect whether the request was made through AJAX.

    In akamatsu this is used to handle some pagination, therefore only a partial
    view is returned instead of the whole HTML.

    In order to detect this, the `x-akamatsu-partial` header should be set to
    "true".

    Returns:
        `True` if the request was made through AJAX, otherwise `False`.
    """
    return request.headers.get('x-akamatsu-partial', 'false') == 'true'
