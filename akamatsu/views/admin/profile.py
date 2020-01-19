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

"""This module contains user profile views."""

from flask import current_app, flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required
from sqlalchemy.exc import IntegrityError

from akamatsu import crypto_manager, db
from akamatsu.views.admin import bp_admin
from akamatsu.forms import PasswordResetForm, ProfileForm


@bp_admin.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """Show user profile edition form."""
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)

        try:
            correct = True
            db.session.commit()

            flash(_('Profile updated correctly'), 'success')

            return render_template('admin/profile/edit.html', form=form)

        except IntegrityError:
            # Email already exists
            correct = False
            form.errors.email.append(_('Email is already registered'))

            return render_template('admin/profile/edit.html', form=form)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to update profile, contact an administrator'), 'error')

            return render_template('admin/profile/edit.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('admin/profile/edit.html', form=form)


@bp_admin.route('/profile/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    """Show form to update user password.

    Requires confirming current password.
    """
    form = PasswordResetForm()

    if form.validate_on_submit():
        # Update user
        current_user.password = crypto_manager.hash(form.password.data)

        try:
            correct = True
            db.session.commit()

            flash(_('Password updated correctly'), 'success')

            return redirect(url_for('admin.profile_edit'))

        except Exception:
            correct = False
            current_app.logger.exception('Failed to update user password')

            flash(_('Error updating password, contact an administrator'), 'error')

            return render_template('admin/profile/change_password.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('admin/profile/change_password.html', form=form)
