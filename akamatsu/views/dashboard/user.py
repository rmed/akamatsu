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

"""This file contains the views for the ``users`` section of the dashboard."""

from akamatsu import db
from akamatsu.forms import UserForm
from akamatsu.models import User
from akamatsu.views.dashboard import bp_dashboard
from akamatsu.util import ROLE_NAMES

from flask import redirect, render_template, request, url_for
from flask_user import roles_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound


@bp_dashboard.route('/users')
@bp_dashboard.route('/users/<int:page>')
@roles_required('admin')
def user_index(page=1):
    """Show list of users registered in the application.

    Args:
        page (int): Listing page number to show.
    """
    order_key, order_dir, ordering = _sort_users(request.args)

    users = (
        User.query
        .order_by(ordering)
        .paginate(page, 20, False))

    try:
        return render_template(
            'akamatsu/dashboard/user/index.html',
            users=users,
            order_key=order_key,
            order_dir=order_dir)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('akamatsu/dashboard/user/index.html')

@bp_dashboard.route('/users/new', methods=['GET', 'POST'])
@roles_required('admin')
def user_create():
    """Show the form for creating a new user."""
    form = UserForm()

    if form.validate_on_submit():
        new_user = User()
        form.populate_obj(new_user)

        # Add roles
        roles = set([n.strip() for n in form.role_list.data.split(',')]) &\
                set(ROLE_NAMES)

        new_user.role_names = roles

        try:
            correct = True
            db.session.add(new_user)
            db.session.commit()

        except SQLAlchemyError as e:
            # Catch SQLAlchemy errors
            correct = False
            errmsg = e.orig

        except Exception as e:
            # Catch anything unknown
            correct = False
            errmsg = 'Unknown error'

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                return render_template(
                    'akamatsu/dashboard/user/edit.html',
                    mode='create',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg)


        # Post saved return to index
        return redirect(url_for('dashboard.user_index'))

    return render_template(
        'akamatsu/dashboard/user/edit.html',
        mode='create',
        form=form)

@bp_dashboard.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@roles_required('admin')
def user_edit(user_id):
    """Show the form for editing an existing user.

    Arguments:
        user_id (int): Unique ID of the user to edit.
    """
    user = User.query.filter_by(id=user_id).first()

    if not user:
        # Return error message
        return render_template(
            'akamatsu/dashboard/user/edit.html',
            mode='edit',
            status='error',
            errmsg='User does not exist')

    form = UserForm(obj=user)
    # Get roles
    form.role_list.data = form.role_list.data or ','.join(user.role_names)

    if form.validate_on_submit():
        # Check model can be saved
        form.populate_obj(user)

        # Add roles
        roles = set([n.strip() for n in form.role_list.data.split(',')]) &\
                set(ROLE_NAMES)

        user.role_names = roles

        try:
            correct = True
            db.session.commit()

        except SQLAlchemyError as e:
            # Catch SQLAlchemy errors
            correct = False
            errmsg = e.orig

        except Exception as e:
            # Catch anything unknown
            correct = False
            errmsg = 'Unknown error'

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                return render_template(
                    'akamatsu/dashboard/user/edit.html',
                    mode='edit',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg,
                    user_id=user_id)

        # Post saved, remain in the edition view
        return render_template(
            'akamatsu/dashboard/user/edit.html',
            mode='edit',
            status='saved',
            form=form,
            user_id=user_id)

    return render_template(
        'akamatsu/dashboard/user/edit.html',
        mode='edit',
        status='edit',
        form=form,
        user_id=user_id)

@bp_dashboard.route('/users/delete/<int:user_id>', methods=['GET', 'POST'])
@roles_required('admin')
def user_delete(user_id):
    """Confirm deletion of a user.

    GET requests show a message to confirm and POST requests delete the page
    and redirect back to index.

    Arguments:
        post_id (int): Unique ID of the page to delete.
    """
    user = User.query.filter_by(id=user_id).first()

    if not user:
        # Show error message
        return render_template(
            'akamatsu/dashboard/user/delete.html', status='error',
            errmsg = 'User with ID %d does not exist' % user_id)

    if request.method == 'POST':
        # Delete post
        try:
            correct = True
            db.session.delete(user)
            db.session.commit()

        except SQLAlchemyError as e:
            # Catch SQLAlchemy errors
            correct = False
            errmsg = e.orig

        except Exception as e:
            # Catch anything unknown
            correct = False
            errmsg = 'Unknown error'

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                return render_template(
                    'akamatsu/dashboard/user/delete.html',
                    status='error',
                    errmsg=errmsg)


        return render_template(
            'akamatsu/dashboard/user/delete.html', status='deleted')

    # Show confirmation
    return render_template(
        'akamatsu/dashboard/user/delete.html', status='confirm', user=user)

def _sort_users(args):
    """Sort users according to the specified key and order.

    Args:
        args(dict): Arguments from the ``request`` object.

    Returns:
        Tuple with key, order and ordering to apply in query ``order_by()``.
    """
    key = args.get('orderby')
    order = args.get('order')
    result = None

    if key == 'email':
        # Order by email
        result = User.email

    elif key == 'enabled':
        # Order by enabled state
        result = User.is_enabled

    elif key == 'firstname':
        # Order by first name
        result = User.first_name

    elif key == 'lastname':
        # Order by ghosting URL
        result = User.last_name

    else:
        # Order by username
        key = 'username'
        result = User.username


    # Ordering
    if order == 'asc':
        return key, order, result

    order = 'desc'
    return key, order, result.desc()
