# -*- coding: utf-8 -*-
#
# akamatsu CMS
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

"""This file contains the blueprint definition for the dashboard."""

from flask import Blueprint, render_template
from flask_user import login_required

bp_dashboard = Blueprint('dashboard', __name__)

@bp_dashboard.route('/')
@login_required
def home():
    """Show the general view of the dashboard."""
    return render_template('akamatsu/dashboard/index.html')

# Import subviews
import akamatsu.views.dashboard.blog
import akamatsu.views.dashboard.file
import akamatsu.views.dashboard.page
import akamatsu.views.dashboard.profile
import akamatsu.views.dashboard.settings
import akamatsu.views.dashboard.user

@bp_dashboard.errorhandler(404)
@login_required
def not_found(e):
    """Show the 404 error."""
    msg = "It's gone! Poof! Magic!"
    return render_template(
        'akamatsu/dashboard/error.html',
        error_code=404,
        error_msg=msg)
