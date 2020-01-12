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

"""This file contains unauthenticated page views."""

from flask import Blueprint, abort, redirect, render_template, url_for

from akamatsu.models import Page


bp_pages = Blueprint('pages', __name__)


@bp_pages.route('/')
def root():
    """Load the root page."""
    page = (
        Page.query
        .filter_by(route='/')
        .filter_by(is_published=True)
    ).first_or_404()

    return render_template('pages/show.html', page=page)


@bp_pages.route('/<path:route>')
def show(route):
    """Show the page identified by the given route.

    Args:
        route (path): Route to the page.
    """
    # Mind root slash
    route = '/' + route

    page = (
        Page.query
        .filter_by(route=route)
        .filter_by(is_published=True)
    ).first_or_404()

    # Check ghost redirection
    if page.ghosted_id is not None:
        if page.ghosted_id == page.id:
            # Prevent loops
            abort(404)

        # Only published pages are allowed
        ghosted = (
            Page.query
            .filter_by(id=page.ghosted_id)
            .filter_by(is_published=True)
        ).first_or_404()

        return redirect(url_for('pages.show', route=ghosted.route))

    return render_template('pages/show.html', page=page)
