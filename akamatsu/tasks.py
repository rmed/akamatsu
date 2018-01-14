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

"""This file contains celery tasks."""

from akamatsu import celery, mail
from flask_mail import Message
from flask_user.emails import send_email


@celery.task()
def async_user_mail(*args):
    """Send Flask-User emails asynchronously."""
    send_email(*args)


@celery.task()
def async_mail(*args, **kwargs):
    """Send Flask-Mail emails asynchronously."""
    message = Message(*args, **kwargs)
    mail.send(message)
