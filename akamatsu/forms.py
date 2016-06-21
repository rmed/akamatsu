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

"""This file contains WTForms form declarations."""

from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateTimeField, \
        StringField, TextAreaField, validators


class PageForm(Form):
    """Form for creating/editing pages."""
    # Basic info
    title = StringField(
        'Page title',
        [validators.Length(min=4, max=255),validators.InputRequired()])

    mini = StringField(
        'Page mini',
        [validators.Length(max=50),],
        default=None)

    content = TextAreaField('Content', description='Markdown/HTML enabled')

    custom_head = TextAreaField(
        'Custom HTML head',
        default=None,
        description='HTML enabled')

    ghost = StringField(
        'Ghost link',
        [validators.Length(max=512),],
        default=None)

    base_route = StringField(
        'Base route',
        [validators.Length(max=255), validators.InputRequired()],
        default='/')

    slug = StringField(
        'Page slug',
        [validators.Length(max=255),])

    # Flags
    is_root = BooleanField('Is root page')
    is_html = BooleanField('Content is HTML')
    use_layout_header = BooleanField('Use layout header')
    is_published = BooleanField('Published')
    comments_enabled = BooleanField('Enable comments')

    # Timestamp
    timestamp = DateTimeField('Publish date')


class PostForm(Form):
    """Form for creating/editing posts."""
    # Basic info
    title = StringField(
        'Post title',
        [validators.Length(min=4, max=255), validators.InputRequired()])

    content = TextAreaField(
        'Content',
        [validators.InputRequired()],
        description='Markdown enabled')

    ghost = StringField(
        'Ghost link',
        [validators.Length(max=512),],
        default=None)

    slug = StringField(
        'Post slug',
        [validators.Length(max=255),])

    # Relational info
    author_name = StringField('Author', description='username')
    tag_list = StringField('Tags', description='comma separated tag names')

    # Flags
    is_published = BooleanField('Published')
    comments_enabled = BooleanField('Enable comments')

    # Timestamp
    timestamp = DateTimeField('Publish date')


class ProfileForm(Form):
    """Form for editing own profile details."""
    first_name = StringField('Name',[validators.Length(max=50)])
    last_name = StringField('Last name',[validators.Length(max=50)])

    email = StringField(
        'Email',
        [validators.Length(max=255), validators.InputRequired(),
         validators.Email()])

    notify_login = BooleanField('Notify login')
    personal_bio = TextAreaField('Personal bio')


class SettingsForm(Form):
    """Form for editing site settings."""
    sitename = StringField('Site name')

    social = TextAreaField(
        'Social links',
        description='format: "glyph-name:URL"')
    navbar = TextAreaField(
        'Navigation bar',
        description='format: "text:URL"')

    allowed_extensions = StringField(
        'Allowed file extensions',
        description='comma separated extensions')

    disqus_shortname = StringField('Disqus shortname')

    footer_left = TextAreaField('Left footer', description='HTML enabled')
    footer_right = TextAreaField('Right footer', description='HTML enabled')


class UploadForm(Form):
    """Form for uploading files."""
    filename = StringField(
        'Filename to use',
        description='if empty, uploaded file name is used')

    subdir = StringField(
        'Subdir for the file',
        description='relative to upload directory in server')

    description = TextAreaField('File description')

    upload = FileField(
        'File to upload',
        [FileRequired()])


class UserForm(Form):
    """Form for showing/editing users (administrator)."""
    # Authentication
    username = StringField(
        'Username',
        [validators.Length(max=50), validators.InputRequired()])

    password = StringField(
        'Password',
        [validators.Length(max=255), validators.InputRequired()])

    reset_password_token = StringField(
        'Password reset token', [validators.Length(max=255)])

    # Email information
    email = StringField(
        'Email',
        [validators.Length(max=255), validators.InputRequired(),
         validators.Email()])

    confirmed_at = DateTimeField('Confirmed at')

    # User information
    is_enabled = BooleanField('Enabled')
    first_name = StringField('Name',[validators.Length(max=50)])
    last_name = StringField('Last name',[validators.Length(max=50)])

    # Additional attributes
    personal_bio = TextAreaField('Personal bio')
    notify_login = BooleanField('Notify login')

    # Relational info
    role_list = StringField('Roles', description='comma separated role names')
