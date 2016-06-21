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

"""This file contains utility functions for akamatsu."""

from flask import current_app, render_template


ROLE_NAMES = ['admin', 'blogger', 'editor', 'uploader']

def is_allowed_file(filename):
    """Check if a file extension is allowed.

    Arguments:
        filename (str): Name of the file to check.
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

def render_theme(template, **kwargs):
    """Render the specified template of the current active theme.

    Arguments:
        template (str): Relative path to the template.
        kwargs (dict): Kwargs for Flask's ``render_template`` funtion.

    Returns:
        Template instance.
    """
    theme_template = '%s/%s' % (current_app.config['THEME'], template)

    return render_template(theme_template, **kwargs)
