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

"""This file contains miscelaneous bootstrap code for akamatsu."""


# Static configuration values
BASE_CONFIG = {
    # Flask-SQLAlchemy
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,

    # Flask-User
    'USER_ENABLE_EMAIL': True,
    'USER_ENABLE_REGISTRATION': False,
    'USER_ENABLE_FORGOT_PASSWORD': True,

    'USER_CHANGE_PASSWORD_TEMPLATE': 'akamatsu/dashboard/flask_user/change_password.html',
    'USER_FORGOT_PASSWORD_TEMPLATE': 'akamatsu/dashboard/flask_user/forgot_password.html',
    'USER_LOGIN_TEMPLATE': 'akamatsu/dashboard/flask_user/login.html',
    'USER_RESET_PASSWORD_TEMPLATE': 'akamatsu/dashboard/flask_user/reset_password.html',

    'USER_CHANGE_PASSWORD_URL': '/dashboard/profile/change-password',
    'USER_EMAIL_ACTION_URL': '/dashboard/users/email/<id>/<action>',
    'USER_FORGOT_PASSWORD_URL': '/dashboard/forgot-password',
    'USER_LOGIN_URL': '/dashboard/login',
    'USER_LOGOUT_URL': '/dashboard/logout',
    'USER_RESET_PASSWORD_URL': '/dashboard/reset-password/<token>',

    'USER_AFTER_CHANGE_PASSWORD_ENDPOINT': 'dashboard.profile_edit',
    'USER_AFTER_FORGOT_PASSWORD_ENDPOINT': 'user.login',
    'USER_AFTER_LOGIN_ENDPOINT': 'dashboard.home',
    'USER_AFTER_RESET_PASSWORD_ENDPOINT': 'dashboard.home',
    'USER_UNAUTHORIZED_ENDPOINT': 'dashboard.home',

    'USER_PASSWORD_HASH': 'sha512_crypt',

    # Cookie notice
    'COOKIE_NOTICE': True,
}

class CeleryWrapper(object):
    """Wrapper for deferred initialization of Celery."""

    def __init__(self):
        self._celery = None
        self.task = None

    def __getattr__(self, attr):
        """Wrap internal celery attributes."""
        if attr == 'make_celery':
            return getattr(self, attr)

        return getattr(self._celery, attr)

    def make_celery(self, app):
        """Create a celery instance for the application.

        Args:
            app: Application instance
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
