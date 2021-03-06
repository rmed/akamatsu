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

"""This module contains page views."""

from urllib.parse import unquote

from flask import abort, current_app, flash, jsonify, redirect, \
        render_template, request, url_for
from flask_babel import _
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from wtforms import ValidationError

from akamatsu import db
from akamatsu.models import Page
from akamatsu.views.admin import bp_admin
from akamatsu.forms import PageForm
from akamatsu.util import allowed_roles, datetime_to_utc, is_ajax, is_safe_url, \
        utc_to_local_tz


@bp_admin.route('/pages')
@allowed_roles('administrator', 'editor')
def page_index():
    """Display a paginated list of pages.

    Only active pages are shown (not ghosts).

    If this endpoint is called from AJAX, only the requested page contents
    are returned.
    """
    page = request.args.get('page', 1, int)
    sort_key = request.args.get('sort')
    order_dir = request.args.get('order')

    pages = (
        Page.query
        .filter(Page.ghosted_id == None)
    )

    pages, sort_key, order_dir = _sort_pages(pages, sort_key, order_dir)
    pages = pages.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if is_ajax():
        # AJAX request
        return render_template(
            'admin/pages/partials/pages_page.html',
            pages=pages,
            sort_key=sort_key,
            order_dir=order_dir
        )

    return render_template(
        'admin/pages/index.html',
        pages=pages,
        sort_key=sort_key,
        order_dir=order_dir
    )


@bp_admin.route('/page-ghosts')
@allowed_roles('administrator', 'editor')
def page_ghosts():
    """Display a paginated list of page ghosts.

    If this endpoint is called from AJAX, only the requested page contents
    are returned.
    """
    page = request.args.get('page', 1, int)
    sort_key = request.args.get('sort')
    order_dir = request.args.get('order')

    pages = (
        Page.query
        .filter(Page.ghosted_id != None)
    )

    pages, sort_key, order_dir = _sort_pages(pages, sort_key, order_dir)
    pages = pages.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if is_ajax():
        # AJAX request
        return render_template(
            'admin/pages/partials/ghosts_page.html',
            pages=pages,
            sort_key=sort_key,
            order_dir=order_dir
        )

    return render_template(
        'admin/pages/ghost_index.html',
        pages=pages,
        sort_key=sort_key,
        order_dir=order_dir
    )


@bp_admin.route('/pages/new', methods=['GET', 'POST'])
@allowed_roles('administrator', 'editor')
def new_page():
    """Create a new page."""
    form = PageForm()

    # Pages available to ghost
    form.ghosted.query = (
        Page.query
        .filter(Page.ghosted_id == None)
        .order_by(Page.title)
    )

    if form.validate_on_submit():
        new_page = Page()
        form.populate_obj(new_page)

        # Adjust timezone
        new_page.last_updated = datetime_to_utc(new_page.last_updated)

        try:
            correct = True
            db.session.add(new_page)
            db.session.commit()

            flash(_('New page created correctly'), 'success')

            return redirect(url_for('admin.page_index'))

        except IntegrityError:
            # Route already exists
            # Need to manually rollback here
            db.session.rollback()
            form.route.errors.append(_('Page route is already in use'))

            return render_template('admin/pages/edit.html', form=form)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to create page, contact an administrator'), 'error')

            return render_template('admin/pages/edit.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('admin/pages/edit.html', form=form)


@bp_admin.route('/pages/<hashid>', methods=['GET', 'POST'])
@allowed_roles('administrator', 'editor')
def edit_page(hashid):
    """Edit an existing page.

    Args:
        hashid (str): HashID of the page.
    """
    page = Page.get_by_hashid(hashid)

    if not page:
        flash(_('Could not find page'), 'error')

        return redirect(url_for('admin.page_index'))

    form = PageForm(obj=page)

    # Pages available to ghost
    form.ghosted.query = (
        Page.query
        .filter(Page.ghosted_id == None)
        .order_by(Page.title)
    )

    if form.validate_on_submit():
        form.populate_obj(page)

        # Adjust timezone
        page.last_updated = datetime_to_utc(page.last_updated)

        try:
            correct = True
            db.session.commit()

            flash(_('Page updated correctly'), 'success')

            return redirect(
                url_for('admin.edit_page', hashid=hashid)
            )

        except IntegrityError:
            # Route already exists
            # Need to manually rollback here
            db.session.rollback()
            form.route.errors.append(_('Page route is already in use'))

            return render_template('admin/pages/edit.html', form=form, page=page)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to update page, contact an administrator'), 'error')

            return render_template('admin/pages/edit.html', form=form, page=page)

        finally:
            if not correct:
                db.session.rollback()


    # First load checks
    if request.method == 'GET':
        # Date
        form.last_updated.data = utc_to_local_tz(form.last_updated.data)

    return render_template('admin/pages/edit.html', form=form, page=page)


@bp_admin.route('/pages/<hashid>/delete', methods=['GET', 'POST'])
@allowed_roles('administrator', 'editor')
def delete_page(hashid):
    """Delete a page.

    Usual flow is by calling this endpoint from AJAX (button in page listing).

    If the query parameter "ref" is set, the browser will be redirected to that
    URL after deletion (if it is safe).

    Args:
        hashid (str): HashID of the page.
    """
    page = Page.get_by_hashid(hashid)

    if not page:
        flash(_('Could not find page'), 'error')

        return redirect(url_for('admin.page_index'))

    if request.method == 'POST':
        # Delete page
        ref = unquote(request.args.get('ref', ''))

        try:
            correct = True
            db.session.delete(page)
            db.session.commit()

            flash(_('Page "%(title)s" deleted', title=page.title), 'success')

            # Redirect user
            if ref and is_safe_url(ref):
                # Provided as query parameter
                if is_ajax():
                    return jsonify({'redirect': ref}), 200

                return redirect(ref)

            # Default to index
            dest = 'admin.page_ghosts' if page.ghosted_id else 'admin.page_index'

            if is_ajax():
                return jsonify({'redirect': url_for(dest)}), 200

            return redirect(url_for(dest))

        except ValidationError:
            # CSRF invalid
            correct = False
            current_app.logger.exception('Failed to delete page')

            flash(_('Failed to delete page, invalid CSRF token received'), 'error')

        except Exception:
            # Catch anything unknown
            correct = False
            current_app.logger.exception('Failed to delete page')

            flash(_('Failed to delete page, unknown error encountered'), 'error')

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                # Check AJAX
                if is_ajax():
                    abort(400)

                return redirect(
                    url_for('admin.edit_page', hashid=hashid)
                )

    # Check AJAX
    if is_ajax():
        return render_template(
            'admin/pages/partials/delete_modal.html',
            page=page,
            ref=request.args.get('ref', '')
        )

    return render_template(
        'admin/pages/delete.html',
        page=page
    )


def _sort_pages(query, key, order):
    """Sort pages according to the specified key and order.

    Args:
        query: Original query to order.
        key (str): Key to order by.
        order (str): Order direction ("asc" or "desc").

    Returns:
        Tuple with ordered query, key, and order.
    """
    ordering = None

    if key == 'title':
        # Order by title
        ordering = Page.title

    elif key == 'route':
        # Order by route
        ordering = Page.route

    elif key == 'published':
        # Order by published state
        ordering = Page.is_published

    elif key == 'comments':
        # Order by comments state
        ordering = Page.comments_enabled

    elif key == 'ghost':
        # Order by ghosted title
        alias = aliased(Page)
        query = (
            query
            .join(alias, Page.ghosted)
        )

        if order == 'asc':
            return query.order_by(alias.title), key, order

        order = 'desc'
        return query.order_by(alias.title.desc()), key, order

    elif key == 'date':
        # Order by date
        ordering = Page.last_updated

    else:
        # Order by date and don't set ordering
        return query.order_by(Page.last_updated.desc()), None, None

    # Ordering
    if order == 'asc':
        return query.order_by(ordering), key, order

    order = 'desc'
    return query.order_by(ordering.desc()), key, order
