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
from flask_migrate import Migrate, MigrateCommand
from flask_misaka import Misaka
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_user import SQLAlchemyAdapter, UserManager, user_logged_in
from flask_waffleconf import AlchemyWaffleStore, WaffleConf

import os


app = Flask(__name__, instance_relative_config=True)

# Load configuration specified in environment variable or default
# development one
# Production configurations shold be stored in `instance/`
if 'AKAMATSU_CONFIG_FILE' in os.environ:
    app.config.from_envvar('AKAMATSU_CONFIG_FILE')

else:
    app.config.from_object('config.development')


# Setup database before importing rest of the application code
db = SQLAlchemy(app)
# Force model registration
from akamatsu import models

# Database migrations
migrate = Migrate(app, db)


# Whitespacing Jinja
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, models.User)
user_manager = UserManager(db_adapter, app)


# Setup Flask-WaffleConf
configstore = AlchemyWaffleStore(db=db, model=models.WaffleModel)
waffle = WaffleConf(app, configstore)


# Misaka markdown parser
md = Misaka(fenced_code=True, underline=True, no_intra_emphasis=False,
        strikethrough=True, superscript=True, tables=True, no_html=True)
md.init_app(app)


# Setup Flask-Mail
mail = Mail(app)


# Flask-Assets bundles
assets = Environment(app)

css_bundle = Bundle(
    'css/fira.css',
    'css/entypo.css',
    'css/highlight-hybrid.css',
    'css/normalize.css',
    'css/simplegrid.css',
    'css/akamatsu.css',
    filters='cssmin', output='gen/packed.css')

# Cannot include zepto, throws errors
js_bundle = Bundle(
    'js/highlight.pack.js',
    'js/akamatsu.js',
    filters='rjsmin', output='gen/packed.js')

db_js_bundle = Bundle(
    'js/dashboard.js',
    filters='rjsmin', output='gen/packed_db.js');

assets.register('css_pack', css_bundle)
assets.register('js_pack', js_bundle)
assets.register('db_js_pack', db_js_bundle)


# Analytics
analytics = Analytics(app)


from akamatsu.views.blog import bp_blog
from akamatsu.views.dashboard import bp_dashboard
from akamatsu.views.misc import bp_misc
from akamatsu.views.page import bp_page
from akamatsu.util import render_theme

# Blueprints
app.register_blueprint(bp_misc)
app.register_blueprint(bp_dashboard, url_prefix='/dashboard')
app.register_blueprint(bp_blog, url_prefix='/blog')
app.register_blueprint(bp_page)


# App commands
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# 404
@app.errorhandler(404)
def not_found(e):
    msg = "It's gone! Poof! Magic!"
    return render_theme('error.html', error_code=404, error_msg=msg)


# Before first request is served
@app.before_first_request
def _do_before_hook():
    """Operations to perform before first request.

    This includes:
        - Updating Flask-WaffleConf config values
    """
    waffle.state.update_conf()

# Signals
@user_logged_in.connect_via(app)
def _do_on_login(sender, user, **extra):
    """Notify the user of a new login.

    This is only done if the ``notify_login`` attribute is set to ``True``.
    """
    if user.notify_login:
        notification = Message(
            'akamatsu - New session started',
            recipients=[user.email],
            body=render_template('mail/login.txt', user=user),
            html=render_template('mail/login.html', user=user))

        mail.send(notification)
