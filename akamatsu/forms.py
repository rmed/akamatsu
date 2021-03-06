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

"""This file contains form definitions."""

import datetime

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateTimeField, PasswordField, StringField, \
        TextAreaField, SubmitField
from wtforms import validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField, \
        QuerySelectMultipleField


# Authentication forms
class LoginForm(FlaskForm):
    """Application login form."""
    identity = StringField(
        _l('Username or email'),
        validators=[
            validators.InputRequired(_l('Identity is required')),
        ]
    )

    password = PasswordField(
        _l('Password'),
        validators=[
            validators.InputRequired(_l('Password is required')),
        ]
    )

    remember_me = BooleanField(_l('Remember me'))

    submit = SubmitField(_l('Sign in'))


class ForgotPasswordForm(FlaskForm):
    """Form to request password reset token."""
    email = StringField(
        _l('Email'),
        validators=[
            validators.InputRequired(_l('Email is required')),
            validators.Email(_l('Invalid Email'))
        ]
    )

    submit = SubmitField(_l('Reset password'))


class ReauthenticationForm(FlaskForm):
    """Reauthentication form."""
    password = PasswordField(
        _l('Password'),
        validators=[
            validators.InputRequired(_l('Password is required')),
        ]
    )

    submit = SubmitField(_l('Sign in'))


class PasswordResetForm(FlaskForm):
    """Reset password form."""
    password = PasswordField(
        _l('New password'),
        validators=[validators.InputRequired(_l('Password is required'))]
    )

    retype_password = PasswordField(
        _l('Retype new password'),
        validators=[
            validators.EqualTo(
                'password',
                message=_l('Passwords did not match')
            )
        ]
    )

    submit = SubmitField(_l('Reset password'))


# CMS forms
class PageForm(FlaskForm):
    """Page form."""
    ghosted = QuerySelectField(_l('Page to ghost'), allow_blank=True)

    title = StringField(
        _l('Title'),
        validators=[
            validators.InputRequired(_l('Page title is required')),
            validators.Length(
                min=3,
                max=255,
                message=_l(
                    'Title length should be between 3 and 255 characters long'
                )
            )
        ]
    )

    mini = StringField(
        _l('Page mini'),
        validators=[
            validators.Length(
                max=50,
                message=_l('Mini should not exceed 50 characters')
            )
        ]
    )

    route = StringField(
        _l('Page route'),
        validators=[
            validators.InputRequired(_l('Page route is required')),
            validators.Length(
                max=255,
                message=_l('Route should not exceed 255 characters')
            )
        ]
    )

    custom_head = TextAreaField(
        _l('Custom HTML head'),
        default=None,
        description=_l('Optional and dangerous, HTML enabled')
    )

    content = TextAreaField(
        _l('Page content'),
        description=_l('Markdown/HTML enabled'),
        validators=[validators.InputRequired(_l('Page content is required'))]
    )

    is_published = BooleanField(_l('Is published'))
    comments_enabled = BooleanField(_l('Enable comments'))

    last_updated = DateTimeField(
        _l('Last updated'),
        description=_l('Will be stored as UTC'),
        format='%Y-%m-%d %H:%M',
        # Will be stored as UTC
        default=datetime.datetime.now()
    )

    submit = SubmitField(_l('Save page'))


class PostForm(FlaskForm):
    """Blog post form."""
    ghosted = QuerySelectField(
        _l('Post to ghost'),
        description=_l('Set to empty to disable ghosting'),
        allow_blank=True
    )
    authors = QuerySelectMultipleField(_l('Additional post author(s)'))

    title = StringField(
        _l('Title'),
        validators=[
            validators.InputRequired(_l('Post title is required')),
            validators.Length(
                min=4,
                max=255,
                message=_l(
                    'Title length should be between 4 and 255 characters long'
                )
            )
        ]
    )

    slug = StringField(
        _l('Post slug'),
        description=_l('Autogenerated if not set'),
        validators=[
            validators.Length(
                max=255,
                message=_l('Slug should not exceed 255 characters')
            )
        ]
    )

    content = TextAreaField(
        _l('Post content'),
        description=_l('Markdown enabled')
    )

    tag_list = StringField(_l('Tag list'))

    is_published = BooleanField(_l('Is published'))
    comments_enabled = BooleanField(_l('Enable comments'))

    last_updated = DateTimeField(
        _l('Last updated'),
        description=_l('Will be stored as UTC'),
        format='%Y-%m-%d %H:%M',
        # Will be stored as UTC
        default=datetime.datetime.now()
    )

    submit = SubmitField(_l('Save post'))


class ProfileForm(FlaskForm):
    """Form for editing own profile details."""
    first_name = StringField(
        _l('First name'),
        validators=[
            validators.Length(
                max=50,
                message=_l('First name should not exceed 50 characters')
            )
        ]
    )

    last_name = StringField(
        _l('Last name'),
        validators=[
            validators.Length(
                max=50,
                message=_l('Last name should not exceed 50 characters')
            )
        ]
    )

    email = StringField(
        _l('Email'),
        description=_l('Must be unique'),
        validators=[
            validators.InputRequired(_l('Email is required')),
            validators.Email(_l('Invalid Email'))
        ]
    )

    notify_login = BooleanField(
        _l('Notify login'),
        description=_l(
            'Receive an email notification each time a session is started'
        )
    )

    personal_bio = TextAreaField(
        _l('Personal bio'),
        description='Markdown enabled'
    )

    submit = SubmitField(_l('Save changes'))


class UploadForm(FlaskForm):
    """Form for uploading files."""
    filename = StringField(
        _l('Name for the stored file'),
        description=_l('If empty, uploaded file name is used'),
        validators=[
            validators.Length(
                max=155,
                message=_l('Filename should not exceed 155 characters')
            )
        ]
    )

    subdir = StringField(
        _l('Subirectory in which to store the file'),
        description=_l('If empty, will use upload root'),
        validators=[
            validators.Length(
                max=100,
                message=_l('Subdirectory should not exceed 100 characters')
            )
        ]
    )

    description = StringField(
        _l('File description'),
        validators=[
            validators.Length(
                max=256,
                message=_l('Description should not exceed 256 characters')
            )
        ]
    )

    mime = StringField(
        _l('MIME type for the file'),
        description=_l('X/Y format, may be inferred from the file if left empty'),
        validators=[
            validators.Length(
                max=128,
                message=_l('MIME type should not exceed 128 characters')
            )
        ]
    )

    upload = FileField(
        _l('Choose a file...'),
        validators=[FileRequired()]
    )

    submit = SubmitField(_l('Save changes'))


class UserForm(FlaskForm):
    """Form for editing users."""
    username = StringField(
        _l('Username'),
        description=_l('Must be unique'),
        validators=[
            validators.InputRequired(_l('Username is required')),
            validators.Length(
                min=3,
                max=50,
                message=_l('Username must be between 3 and 50 characters long')
            )
        ]
    )

    password = PasswordField(
        _l('Password'),
        description=_l('If empty, a random password will be generated')
    )

    email = StringField(
        _l('Email'),
        description=_l('Must be unique'),
        validators=[
            validators.InputRequired(_l('Email is required')),
            validators.Email(_l('Invalid Email'))
        ]
    )

    is_active = BooleanField(_l('Is active'))
    notify_login = BooleanField(
        _l('Notify login'),
        description=_l(
            'Receive an email notification each time a session is started'
        )
    )

    first_name = StringField(
        _l('First name'),
        validators=[
            validators.Length(
                max=50,
                message=_l('First name should not exceed 50 characters')
            )
        ]
    )

    last_name = StringField(
        _l('Last name'),
        validators=[
            validators.Length(
                max=50,
                message=_l('Last name should not exceed 50 characters')
            )
        ]
    )

    personal_bio = TextAreaField(
        _l('Personal bio'),
        description='Markdown enabled'
    )

    roles = QuerySelectMultipleField(_l('User roles'))

    submit = SubmitField(_l('Save user'))
