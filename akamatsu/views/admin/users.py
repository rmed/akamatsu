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

"""This module contains user views."""

from urllib.parse import unquote

from flask import abort, current_app, flash, jsonify, redirect, \
        render_template, request, url_for
from flask_babel import _
from passlib import pwd
from sqlalchemy.exc import IntegrityError
from wtforms import ValidationError

from akamatsu import crypto_manager, db
from akamatsu.models import User, Role
from akamatsu.views.admin import bp_admin
from akamatsu.forms import UserForm
from akamatsu.util import allowed_roles, is_safe_url


@bp_admin.route('/users')
@allowed_roles('administrator')
def user_index():
    """Display a paginated list of users.

    If this endpoint is called from AJAX, only the requested page contents
    are returned.
    """
    page = request.args.get('page', 1, int)
    sort_key = request.args.get('sort')
    order_dir = request.args.get('order')

    users = User.query

    users, sort_key, order_dir = _sort_users(users, sort_key, order_dir)
    users = users.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if request.is_xhr:
        # AJAX request
        return render_template(
            'admin/users/partials/users_page.html',
            users=users,
            sort_key=sort_key,
            order_dir=order_dir
        )

    return render_template(
        'admin/users/index.html',
        users=users,
        sort_key=sort_key,
        order_dir=order_dir
    )


@bp_admin.route('/users/new', methods=['GET', 'POST'])
@allowed_roles('administrator')
def new_user():
    """Create a new user."""
    form = UserForm()

    # Pages available to ghost
    form.roles.query = (
        Role.query
        .order_by(Role.name)
    )

    if form.validate_on_submit():
        new_user = User()
        form.populate_obj(new_user)

        if not form.password.data:
            # Generate password
            new_user.password = crypto_manager.hash(pwd.genword(length=12))
        else:
            # Hash password
            new_user.password = crypto_manager.hash(form.password.data)

        try:
            correct = True
            db.session.add(new_user)
            db.session.commit()

            flash(_('New user created correctly'), 'success')

            return redirect(url_for('admin.user_index'))

        except IntegrityError:
            # Either email or username already exist
            # Need to manually rollback here
            db.session.rollback()
            form.username.errors.append(_('Username may already be in use'))
            form.email.errors.append(_('Email may already be in use'))

            return render_template('admin/users/edit.html', form=form)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to create user, contact an administrator'), 'error')

            return render_template('admin/user/edit.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('admin/users/edit.html', form=form)


@bp_admin.route('/users/<username>', methods=['GET', 'POST'])
@allowed_roles('administrator')
def edit_user(username):
    """Edit an existing user.

    Args:
        username (str): Username of the user
    """
    user = User.get_by_username(username)

    if not user:
        flash(_('Could not find user'), 'error')

        return redirect(url_for('admin.user_index'))

    form = UserForm(obj=user)

    # Override password
    form.password.description = _('Leave empty if unchanged')

    form.roles.query = (
        Role.query
        .order_by(Role.name)
    )

    if form.validate_on_submit():
        _orig_pass = user.password
        form.populate_obj(user)

        user.password = _orig_pass

        # Hash password (if present)
        if form.password.data:
            user.password = crypto_manager.hash(form.password.data)

        try:
            correct = True
            db.session.commit()

            flash(_('User updated correctly'), 'success')

            return redirect(
                url_for('admin.edit_user', username=username)
            )

        except IntegrityError:
            # Either email or username already exist
            # Need to manually rollback here
            db.session.rollback()
            form.username.errors.append(_('Username may already be in use'))
            form.email.errors.append(_('Email may already be in use'))

            return render_template('admin/users/edit.html', form=form, user=user)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to update user, contact an administrator'), 'error')

            return render_template('admin/users/edit.html', form=form, user=user)

        finally:
            if not correct:
                db.session.rollback()


    # First load checks
    if request.method == 'GET':
        # Password
        form.password.data = ''

    return render_template('admin/users/edit.html', form=form, user=user)


@bp_admin.route('/users/<username>/delete', methods=['GET', 'POST'])
@allowed_roles('administrator')
def delete_user(username):
    """Delete a user.

    Usual flow is by calling this endpoint from AJAX (button in post listing).

    If the query parameter "ref" is set, the browser will be redirected to that
    URL after deletion (if it is safe).

    Args:
        username (str): Username of the user
    """
    user = User.get_by_username(username)

    if not user:
        flash(_('Could not find user'), 'error')

        return redirect(url_for('admin.user_index'))

    if request.method == 'POST':
        # Delete user
        ref = unquote(request.args.get('ref', ''))

        try:
            correct = True
            db.session.delete(user)
            db.session.commit()

            flash(_('User "%(username)s" deleted', username=username), 'success')

            # Redirect user
            if ref and is_safe_url(ref):
                # Provided as query parameter
                if request.is_xhr:
                    return jsonify({'redirect': ref}), 200

                return redirect(ref)

            # Default to index
            if request.is_xhr:
                return jsonify({'redirect': url_for('admin.user_index')}), 200

            return redirect(url_for('admin.user_index'))

        except ValidationError:
            # CSRF invalid
            correct = False
            current_app.logger.exception('Failed to delete user')

            flash(_('Failed to delete user, invalid CSRF token received'), 'error')

        except Exception:
            # Catch anything unknown
            correct = False
            current_app.logger.exception('Failed to delete user')

            flash(_('Failed to delete user, unknown error encountered'), 'error')

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                # Check AJAX
                if request.is_xhr:
                    abort(400)

                return redirect(
                    url_for('admin.edit_user', username=username)
                )

    # Check AJAX
    if request.is_xhr:
        return render_template(
            'admin/users/partials/delete_modal.html',
            user=user,
            ref=request.args.get('ref', '')
        )

    return render_template(
        'admin/users/delete.html',
        user=user
    )


def _sort_users(query, key, order):
    """Sort users according to the specified key and order.

    Args:
        query: Original query to order.
        key (str): Key to order by.
        order (str): Order direction ("asc" or "desc").

    Returns:
        Tuple with key, order and ordered query.
    """
    ordering = None

    if key == 'username':
        # Order by username
        ordering = User.username

    elif key == 'email':
        # Order by email
        ordering = User.email

    elif key == 'first_name':
        # Order by first name
        ordering = User.first_name

    elif key == 'last_name':
        # Order by last name
        ordering = User.last_name

    elif key == 'active':
        # Order by user status
        ordering = User.is_active

    else:
        # Order by username and don't set ordering
        return query.order_by(User.username.desc()), None, None

    # Ordering
    if order == 'asc':
        return query.order_by(ordering), key, order

    order = 'desc'
    return query.order_by(ordering.desc()), key, order
