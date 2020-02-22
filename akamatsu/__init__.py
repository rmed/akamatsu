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

"""This file contains initialization code."""

import os

from babel import dates as babel_dates
from flask import Flask, current_app
from flask_analytics import Analytics
from flask_assets import Environment, Bundle
from flask_babel import Babel, _
from flask_discussion import Discussion
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

import flask
import pytz
import webassets

from akamatsu.bootstrap import BASE_CONFIG
from akamatsu.errors import forbidden, page_not_found, server_error
from akamatsu.util import CeleryWrapper, CryptoManager, HashidsWrapper, \
        HighlighterRenderer

__version__ = '2.0.0'


# Debug toolbar (for development)
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension()

    _USING_TOOLBAR = True

except ImportError:
    _USING_TOOLBAR = False


# Crypto
crypto_manager = CryptoManager()

# Hashids
hashids_hasher = HashidsWrapper()

# Babel
babel = Babel()

# CSRF
csrf = CSRFProtect()

# SQLAlchemy
db = SQLAlchemy()

# Flask-Migrate
migrate = Migrate()

# Flask-Mail
mail = Mail()

# Flask-Login
login_manager = LoginManager()

# Flask-Misaka
md = Misaka(
    renderer=HighlighterRenderer(),
    fenced_code=True,
    underline=True,
    no_intra_emphasis=False,
    strikethrough=True,
    superscript=True,
    tables=True
)

# Flask-Assets
assets = Environment()

# Celery
celery = CeleryWrapper()

# Flask-Discussion
discussion = Discussion()


@babel.localeselector
def get_locale():
    """Get locale from config."""
    return current_app.config.get('LOCALE', 'en')


def url_for_self(**kwargs):
    """Helper to return current endpoint in Jinja template."""
    return flask.url_for(
        flask.request.endpoint,
        **dict(flask.request.view_args, **kwargs)
    )


def format_datetime(value):
    """Jinja filter to format datetime using app defined timezone.

    If not a valid timezone, defaults to UTC.

    Args:
        value (datetime): Datetime object to represent.
    """
    app_tz = current_app.config.get('TIMEZONE', 'UTC')

    if not app_tz in pytz.common_timezones:
        app_tz = 'UTC'

    tz = babel_dates.get_timezone(app_tz)

    return babel_dates.format_datetime(
        value,
        'yyyy-MM-dd HH:mm z',
        tzinfo=tz
    )


def init_app():
    """Initialize app."""
    app = Flask(__name__)
    app.config.update(BASE_CONFIG)

    # Load configuration specified in environment variable or default
    # development one.
    # Production configurations shold be stored in a separate directory, such
    # as `instance`.
    if 'AKAMATSU_CONFIG' in os.environ:
        app.config.from_envvar('AKAMATSU_CONFIG')

    else:
        # Development environment
        from akamatsu.bootstrap import DEV_CONFIG
        app.config.update(DEV_CONFIG)

    app.config['__version__'] = __version__


    # Custom jinja helpers
    app.jinja_env.globals['url_for_self'] = url_for_self
    app.jinja_env.filters['datetime'] = format_datetime


    # Whitespacing Jinja
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True


    # Setup debug toolbar in development
    if app.config.get('DEBUG') and _USING_TOOLBAR:
        toolbar.init_app(app)

    # Setup cryptography (passlib)
    crypto_manager.init_app(app)


    # Setup Hashids
    hashids_hasher.init_app(app)


    # Setup localization
    babel.init_app(app)


    # Setup CSRF protection
    csrf.init_app(app)


    # Setup database
    db.init_app(app)
    # Force model registration
    from akamatsu import models

    # Database migrations
    migrations_dir = os.path.join(app.root_path, 'migrations')
    migrate.init_app(app, db, migrations_dir)


    # Setup Flask-Mail
    mail.init_app(app)


    # Setup Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = _('Please login to continue')
    login_manager.login_message_category = 'info'
    login_manager.refresh_view = 'auth.reauthenticate'
    login_manager.needs_refresh_message = (
        _('To protect your account, please reauthenticate to access this page.')
    )
    login_manager.needs_refresh_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.get_by_id(user_id)


    # Enable Celery support (optional)
    if app.config.get('USE_CELERY', False):
        celery.init_app(app)

        # Import tasks
        from akamatsu.async_tasks import async_mail


    # Setup Flask-Misaka
    md.init_app(app)


    # Setup Flask-Assets and bundles
    assets.init_app(app)
    libsass = webassets.filter.get_filter(
        'libsass',
        style='compressed'
    )

    scss_bundle = Bundle(
        # Bulma 0.8.0
        # Builma-Divider 0.2.0
        # Bulma-Switch 1.0.2
        # Bulma-Tagsinput 1.0.11
        # Font Awesome 5.12.0
        'app.scss',
        depends='scss/custom.scss',
        filters=libsass
    )

    css_bundle = Bundle(
        scss_bundle,
        filters='cssmin',
        output='gen/packed.css'
    )

    admin_css_bundle = Bundle(
        'css/vendor/easymde.css',
        output='gen/packed_admin.css'
    )

    js_bundle = Bundle(
        'js/vendor/zepto.min.js', # 1.2.0
        'js/vendor/noty.min.js', # 3.2.0-beta
        'js/navigation.js',
        'js/init.js',
        filters='rjsmin',
        output='gen/packed.js'
    )

    pre_admin_js_bundle = Bundle(
        'js/vendor/bulma-tagsinput.min.js', # 1.0.11
        'js/vendor/bulma-calendar.min.js', # 6.0.3
        'js/admin/navigation.js',
        'js/admin/init.js',
        filters='rjsmin'
    )

    admin_js_bundle = Bundle(
        'js/vendor/easymde.min.js', # 2.9.0
        pre_admin_js_bundle,
        output='gen/packed_admin.js'
    )


    assets.register('css_pack', css_bundle)
    assets.register('js_pack', js_bundle)
    assets.register('admin_css_pack', admin_css_bundle)
    assets.register('admin_js_pack', admin_js_bundle)


    # Setup Flask-Analytics (does not need to be global)
    if app.config.get('USE_ANALYTICS'):
        analytics = Analytics(app)


    # Setup Flask-Discussion
    discussion.init_app(app)


    # Register blueprints
    from akamatsu.views.auth import bp_auth
    from akamatsu.views.admin import bp_admin
    from akamatsu.views.blog import bp_blog
    from akamatsu.views.common import bp_common
    from akamatsu.views.pages import bp_pages

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_admin, url_prefix='/admin')
    app.register_blueprint(bp_blog, url_prefix='/blog')
    app.register_blueprint(bp_common)
    app.register_blueprint(bp_pages)


    # Custom commands
    from akamatsu import commands


    # Custom error handlers
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, server_error)


    return app
