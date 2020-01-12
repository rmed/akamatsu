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

"""This file contains authentication-related views."""

import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, \
    request, url_for
from flask_babel import _
from flask_login import confirm_login, current_user, login_user, logout_user, \
    login_required
from passlib import pwd
from sqlalchemy import or_

from akamatsu import db, crypto_manager
from akamatsu.forms import LoginForm, ForgotPasswordForm, \
    ReauthenticationForm, PasswordResetForm
from akamatsu.models import User
from akamatsu.util import is_safe_url, send_email


bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/dashboard/login', methods=['GET', 'POST'])
def login():
    """Log the user in."""
    form = LoginForm()

    if form.validate_on_submit():
        # Check credentials
        user = (
            User.query
            .filter(
                or_(
                    User.username==form.identity.data,
                    User.email==form.identity.data
                )
            )
        ).first()

        if not user or not crypto_manager.verify(form.password.data, user.password):
            # Show invalid credentials message
            flash(_('Invalid credentials'), 'error')

            return render_template('auth/login.html', form=form)

        # Log the user in
        if login_user(user, remember=form.remember_me.data):
            flash(_('Logged in successfully'), 'success')

            if user.notify_login:
                # Send notification email
                send_email(
                    _('akamatsu - New session started'),
                    recipients=[user.email],
                    body=render_template(
                        'email/auth/login_notification.txt',
                        user=user
                    )
                )

            # Validate destination
            next_url = request.args.get('next')

            if next_url and is_safe_url(next_url):
                return redirect(next_url)

            return redirect(url_for('dashboard.home'))

        # User is not allowed
        flash(_('Invalid credentials'), 'error')

    return render_template('auth/login.html', form=form)


@bp_auth.route("/dashboard/logout")
@login_required
def logout():
    """Log the user out."""
    logout_user()

    return redirect(url_for('auth.login'))


@bp_auth.route('/dashboard/reauthenticate', methods=['GET', 'POST'])
@login_required
def reauthenticate():
    """Ask the user to confirm their password."""
    form = ReauthenticationForm()

    if form.validate_on_submit():
        # Check credentials
        if crypto_manager.verify(form.password.data, current_user.password):
            # Show invalid credentials message
            flash(_('Invalid credentials'), 'error')

            return render_template('auth/reauthenticate.html', form=form)

        # Refresh session
        confirm_login()


        # Validate destination
        next_url = request.args.get('next')

        if next_url and is_safe_url(next_url):
            return redirect(next_url)

        return redirect(url_for('dashboard.home'))

    return render_template('auth/reauthenticate.html', form=form)


@bp_auth.route('/auth/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Show a form to request a password reset token.

    This does not tell the user whether the emails is valid or not. In
    addition, if the user already had a password reset token, it will be
    overwritten.
    """
    if current_user.is_authenticated:
        # Authenticated user cannot do this
        logout_user()

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        # Verify user (must be active)
        user = (
            User.query
            .filter_by(email=form.email.data)
            .filter_by(is_active=True)
        ).first()

        if not user:
            # Don't let the user know
            flash(_('A password reset token has been sent'), 'success')
            return render_template('auth/forgot_password.html', form=form)

        # Set token
        token = pwd.genword(entropy='strong', length=100, charset='hex')

        user.password_reset_token = token
        user.reset_expiration = (
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )

        try:
            correct = True
            db.session.commit()

            # Send notification email
            send_email(
                _('Password reset'),
                recipients=[user.email],
                body=render_template(
                    'email/auth/forgot_password.txt',
                    user=user,
                    token=token
                )
            )

            flash(_('A password reset token has been sent'), 'success')
            return render_template('auth/forgot_password.html', form=form)

        except Exception:
            correct = False
            current_app.logger.exception(
                'Failed to update password reset token for %s' % user.username
            )

            # Don't let the user know
            flash(_('A password reset token has been sent'), 'success')
            return render_template('auth/forgot_password.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('auth/forgot_password.html', form=form)


@bp_auth.route('/auth/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Show a form to reset account password.

    Args:
        token (str): Random token mailed to the user.
    """
    if current_user.is_authenticated:
        # Authenticated user cannot do this
        logout_user()

    # Verify token
    now = datetime.datetime.utcnow()
    user = (
        User.query
        .filter_by(reset_password_token=token)
        .filter_by(is_active=True)
        .filter(User.reset_expiration >= now)
    ).first()

    if not user:
        flash(_('Invalid password reset token provided'), 'error')
        return redirect(url_for('auth.login'))

    # Show form
    form = PasswordResetForm()

    if form.validate_on_submit():
        # Update user
        user.password = crypto_manager.hash(form.password.data)

        try:
            correct = True
            db.session.commit()

            # Send notification email
            send_email(
                _('Password reset notification'),
                recipients=[user.email],
                body=render_template(
                    'email/auth/password_changed.txt',
                    user=user
                )
            )

            flash(_('Password updated, you may now login'), 'success')
            return redirect(url_for('auth.login'))

        except Exception:
            correct = False
            current_app.logger.exception('Failed to reset user password')

            flash(_('Error updating password, contact an admin'), 'error')
            return render_template('auth/reset_password.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('auth/reset_password.html', form=form)
