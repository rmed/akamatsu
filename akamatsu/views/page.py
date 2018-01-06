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

"""This file contains unauthenticated page views."""

from flask import Blueprint, redirect, url_for

from akamatsu.models import Page
from akamatsu.util import render_theme

bp_page = Blueprint('page', __name__)


@bp_page.route('/')
def root():
    """Load the root of the website.

    Only the first page flagged with ``is_root`` is considered.
    """
    page = Page.query.filter_by(is_root=True).first_or_404()

    return render_theme('page/show.html', page=page)

@bp_page.route('/<path:path>')
def show(path):
    """Show the page identified by the given route.

    The path is checked against the ``route`` attribute of the Page model.

    Arguments:
        path (path): Path to a page. The page (if found) is checked to see
            if it has been made public.
    """
    # Mind root slash
    route = '/' + path

    page = Page.query.filter_by(route=route, is_published=True).first_or_404()

    # Check ghost redirection
    if page.ghost:
        # Redirect (301) to new page
        if page.ghost.startswith('/'):
            redirected_path = page.ghost
        else:
            redirected_path = '/' + page.ghost

        return redirect(url_for('page.show', path=redirected_path), 301)

    return render_theme('page/show.html', page=page)
