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

"""This module contains administration views."""

from flask import Blueprint, render_template
from flask_babel import _
from flask_login import current_user, login_required

from akamatsu.models import FileUpload, Page, Post, User, user_posts


bp_admin = Blueprint('admin', __name__)


@bp_admin.route('/')
@login_required
def home():
    """Show admin dashboard."""
    params = {}

    if current_user.has_role('administrator'):
        params['posts'] = (
            Post.query
            .filter(Post.ghosted_id == None)
        ).count()

        params['post_ghosts'] = (
            Post.query
            .filter(Post.ghosted_id != None)
        ).count()

        params['pages'] = (
            Page.query
            .filter(Page.ghosted_id == None)
        ).count()

        params['page_ghosts'] = (
            Page.query
            .filter(Page.ghosted_id != None)
        ).count()

        params['files'] = FileUpload.query.count()

        params['users'] = User.query.count()

    else:
        if current_user.has_role('blogger'):
            params['posts'] = (
                Post.query
                .join(user_posts)
                .join(User)
                .filter(User.id == current_user.id)
                .filter(Post.ghosted_id == None)
            ).count()

            params['post_ghosts'] = (
                Post.query
                .join(user_posts)
                .join(User)
                .filter(User.id == current_user.id)
                .filter(Post.ghosted_id != None)
            ).count()

        if current_user.has_role('editor'):
            params['pages'] = (
                Page.query
                .filter(Page.ghosted_id == None)
            ).count()

            params['page_ghosts'] = (
                Page.query
                .filter(Page.ghosted_id != None)
            ).count()

        if current_user.has_role('blogger') or current_user.has_role('editor'):
            params['files'] = FileUpload.query.count()

    return render_template('admin/index.html', **params)


# Import subviews
from akamatsu.views.admin import files
from akamatsu.views.admin import pages
from akamatsu.views.admin import posts
from akamatsu.views.admin import profile
from akamatsu.views.admin import users


@bp_admin.errorhandler(404)
@login_required
def dashboard_not_found(e):
    return render_template(
        'admin/error.html',
        error_msg=_('It\'s gone! Poof! Magic!')
    ), 404
