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

"""This file contains the views for the ``pages`` section of the dashboard."""

from akamatsu import db
from akamatsu.forms import PageForm
from akamatsu.models import Page
from akamatsu.views.dashboard import bp_dashboard

from flask import redirect, render_template, request, url_for
from flask_user import roles_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound


@bp_dashboard.route('/pages')
@bp_dashboard.route('/pages/<int:page>')
@roles_required(['admin', 'editor'])
def page_index(page=1):
    """Display list of pages (paginated and available options).

    Ghosts are not displayed in this list.

    Args:
        page (int): Listing page number to show.
    """
    order_key, order_dir, ordering = _sort_pages(request.args)

    pages = (
        Page.query
        .filter_by(ghost='')
        .order_by(ordering)
        .paginate(page, 20, False))

    try:
        return render_template(
            'akamatsu/dashboard/page/index.html',
            pages=pages,
            order_key=order_key,
            order_dir=order_dir)

    except NotFound:
        # Show a 'no pages found' notice instead of a 404 error
        return render_template('akamatsu/dashboard/page/index.html')

@bp_dashboard.route('/pages/ghosts')
@bp_dashboard.route('/pages/ghosts/<int:page>')
@roles_required(['admin', 'editor'])
def page_ghost_index(page=1):
    """Display list of ghost pages (paginated and available options).

    Args:
        page (int): Listing page number to show.
    """
    order_key, order_dir, ordering = _sort_pages(request.args)

    pages = (
        Page.query
        .filter(Page.ghost!='')
        .order_by(ordering)
        .paginate(page, 20, False))

    try:
        return render_template(
            'akamatsu/dashboard/page/ghost_index.html',
            pages=pages,
            order_key=order_key,
            order_dir=order_dir)

    except NotFound:
        # Show a 'no pages found' notice instead of a 404 error
        return render_template('akamatsu/dashboard/page/ghost_index.html')

@bp_dashboard.route('/pages/new', methods=['GET', 'POST'])
@roles_required(['admin', 'editor'])
def page_create():
    """Show the form for creating a new post."""
    form = PageForm()

    if form.validate_on_submit():
        new_page = Page()
        form.populate_obj(new_page)

        try:
            correct = True
            db.session.add(new_page)
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
                    'akamatsu/dashboard/page/edit.html',
                    mode='create',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg)


        # Page saved return to index
        return redirect(url_for('dashboard.page_index'))

    return render_template('akamatsu/dashboard/page/edit.html', form=form)

@bp_dashboard.route('/pages/edit/<int:page_id>', methods=['GET', 'POST'])
@roles_required(['admin', 'editor'])
def page_edit(page_id):
    """Show the form for editing an existing page.

    Arguments:
        page_id (int): Unique ID of the page to edit.
    """
    page = Page.query.filter_by(id=page_id).first()

    if not page:
        # Return error message
        return render_template(
            mode='edit',
            status='error',
            errmsg='Page does not exist')

    form = PageForm(obj=page)

    if form.validate_on_submit():
        # Update model
        form.populate_obj(page)

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
                    'akamatsu/dashboard/page/edit.html',
                    mode='edit',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg,
                    page_id=page_id)


        # Page saved, remain in edition view
        return render_template(
            'akamatsu/dashboard/page/edit.html',
            mode='edit',
            status='saved',
            form=form,
            page_id=page_id)

    return render_template(
        'akamatsu/dashboard/page/edit.html',
        mode='edit',
        status='edit',
        form=form,
        page_id=page_id)

@bp_dashboard.route('/pages/delete/<int:page_id>', methods=['GET', 'POST'])
@roles_required(['admin', 'editor'])
def page_delete(page_id):
    """Confirm deletion of a page.

    GET requests show a message to confirm and POST requests delete the page
    and redirect back to index.

    Arguments:
        post_id (int): Unique ID of the page to delete.
    """
    page = Page.query.filter_by(id=page_id).first()

    if not page:
        # Show error message
        return render_template(
            'akamatsu/dashboard/page/delete.html', status='error',
            errmsg = 'Page with ID %d does not exist' % page_id)

    if request.method == 'POST':
        # Delete post
        try:
            correct = True
            db.session.delete(page)
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
                    'akamatsu/dashboard/page/delete.html',
                    status='error',
                    errmsg=errmsg)


        return render_template(
            'akamatsu/dashboard/page/delete.html', status='deleted')

    # Show confirmation
    return render_template(
        'akamatsu/dashboard/page/delete.html', status='confirm', page=page)

def _sort_pages(args):
    """Sort pages according to the specified key and order.

    Args:
        args(dict): Arguments from the ``request`` object.

    Returns:
        Tuple with key, order and ordering to apply in query ``order_by()``.
    """
    key = args.get('orderby')
    order = args.get('order')
    result = None

    if key == 'title':
        # Order by title
        result = Page.title

    elif key == 'route':
        # Order by route
        result = Page.route

    elif key == 'published':
        # Order by published state
        result = Page.is_published

    elif key == 'comments':
        # Order by comments state
        result = Page.comments_enabled

    elif key == 'ghost':
        # Order by ghosting URL
        result = Page.ghost

    else:
        # Order by date
        key = 'date'
        result = Page.timestamp


    # Ordering
    if order == 'asc':
        return key, order, result

    order = 'desc'
    return key, order, result.desc()
