# -*- coding: utf-8 -*-
#
# Akamatsu CMS
# https://github.com/rmed/akamatsu
#
# Copyright (C) 2016 Rafael Medina García <rafamedgar@gmail.com>
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

"""This file contains initialization code for akamatsu."""

from flask import Flask, render_template
from flask_analytics import Analytics
from flask_assets import Environment, Bundle
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy
from flask_user import SQLAlchemyAdapter, UserManager, user_logged_in
from flask_user.emails import send_email

from akamatsu.bootstrap import BASE_CONFIG, CeleryWrapper
from akamatsu.util import HighlighterRenderer

import os


# SQLAlchemy
db = SQLAlchemy()
# Flask-Migrate
migrate = Migrate()
# Flask-Mail
mail = Mail()
# Celery (optional)
celery = CeleryWrapper()
# Flask-User
user_manager = UserManager()
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


def init_app():
    """Initialize akamatsu."""
    app = Flask(__name__)
    app.config.update(BASE_CONFIG)

    # Load configuration specified in environment variable or default
    # development one.
    # Production configurations shold be stored in a separate directory, such
    # as `instance`.
    if 'AKAMATSU_CONFIG' in os.environ:
        app.config.from_envvar('AKAMATSU_CONFIG')

    else:
        app.config.from_object('akamatsu.config.development')

    # Whitespacing Jinja
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True


    # Setup database
    db.init_app(app)
    # Force model registration
    from akamatsu import models

    # Database migrations
    migrate.init_app(app, db)


    # Setup Flask-Mail
    mail.init_app(app)


    # Celery support (optional)
    if app.config.get('USE_CELERY', False):
        celery.make_celery(app)

        # Import tasks
        from akamatsu.tasks import async_user_mail, async_mail


    # Setup Flask-User
    def _send_user_mail(*args):
        """Specify the function for sending mails in Flask-User.

        If celery has been initialized, this will be asynchronous. Defaults to
        the original one in Flask-User.
        """
        if app.config.get('USE_CELERY', False):
            # Asynchronous
            async_user_mail.delay(*args)

        else:
            # Synchronous
            send_email(*args)


    user_db_adapter = SQLAlchemyAdapter(db, models.User)
    user_manager.init_app(
        app,
        db_adapter=user_db_adapter,
        send_email_function=_send_user_mail
    )


    # Setup Flask-Misaka
    md.init_app(app)


    # Setup Flask-Assets and bundles
    assets.init_app(app)

    css_bundle = Bundle(
        'css/fira.css',
        'css/font-awesome.min.css',
        'css/highlight.css',
        'css/normalize.css',
        'css/simplegrid.css',
        'css/akamatsu.css',
        filters='cssmin',
        output='gen/packed.css'
    )

    # Cannot include zepto, throws errors
    js_bundle = Bundle(
        'js/akamatsu.js',
        filters='rjsmin',
        output='gen/packed.js'
    )

    db_js_bundle = Bundle(
        'js/dashboard.js',
        filters='rjsmin',
        output='gen/packed_db.js'
    )

    assets.register('css_pack', css_bundle)
    assets.register('js_pack', js_bundle)
    assets.register('db_js_pack', db_js_bundle)


    # Setup Flask-Analytics (does not need to be global)
    analytics = Analytics(app)


    # Register blueprints
    from akamatsu.views.blog import bp_blog
    # from akamatsu.views.dashboard import bp_dashboard
    from akamatsu.views.misc import bp_misc
    from akamatsu.views.page import bp_page
    from akamatsu.util import render_theme

    app.register_blueprint(bp_misc)
    # app.register_blueprint(bp_dashboard, url_prefix='/dashboard')
    app.register_blueprint(bp_blog, url_prefix='/blog')
    app.register_blueprint(bp_page)


    # Custom commands
    from akamatsu import commands


    # 404
    @app.errorhandler(404)
    def not_found(e):
        msg = "It's gone! Poof! Magic!"
        return render_theme('error.html', error_code=404, error_msg=msg)


    # Signals
    @user_logged_in.connect_via(app)
    def _do_on_login(sender, user, **extra):
        """Notify the user of a new login.

        This is only done if the ``notify_login`` attribute is set to ``True``.

        If Celery is enabled, the message will be sent asynchronously.
        """
        if user.notify_login:
            notification = Message(
                'akamatsu - New session started',
                recipients=[user.email],
                body=render_template('mail/login.txt', user=user),
                html=render_template('mail/login.html', user=user)
            )

            if app.config.get('USE_CELERY', False):
                async_mail.delay(notification)
            else:
                mail.send(notification)


    return app
