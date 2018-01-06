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

"""This file contains the views for the ``blog`` section of the dashboard."""

from flask import redirect, render_template, request, url_for
from flask_user import current_user, roles_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound

from akamatsu import db
from akamatsu.forms import PostForm
from akamatsu.models import Post, User
from akamatsu.views.dashboard import bp_dashboard


@bp_dashboard.route('/blog')
@bp_dashboard.route('/blog/<int:page>')
@roles_required(['admin', 'blogger', 'superblogger'])
def blog_index(page=1):
    """Display list of posts (paginated and available options).

    Ghosts are not displayed in this list.

    Args:
        page (int): Listing page number to show.
    """
    order_key, order_dir, ordering = _sort_posts(request.args)

    filters = {
        'ghost': '',
    }

    # Regular bloggers can only see their own posts
    if current_user.has_role('blogger'):
        filters['author_id'] = current_user.id

    posts = (
        Post.query
        .filter_by(**filters)
        .order_by(ordering)
        .paginate(page, 20, False)
    )

    try:
        return render_template(
            'akamatsu/dashboard/blog/index.html',
            posts=posts,
            order_key=order_key,
            order_dir=order_dir
        )

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('akamatsu/dashboard/blog/index.html')

@bp_dashboard.route('/blog/ghosts')
@bp_dashboard.route('/blog/ghosts/<int:page>')
@roles_required(['admin', 'blogger', 'superblogger'])
def blog_ghost_index(page=1):
    """Display list of ghost posts (paginated and available options).

    Args:
        page (int): Listing page number to show.
    """
    order_key, order_dir, ordering = _sort_posts(request.args)

    filters = (Post.ghost != '',)

    # Regular bloggers can only see their own posts
    if current_user.has_role('blogger'):
        filters = filters + (Post.author_id == current_user.id, )

    posts = (
        Post.query
        .filter(*filters)
        .order_by(ordering)
        .paginate(page, 20, False)
    )

    try:
        return render_template(
            'akamatsu/dashboard/blog/ghost_index.html',
            posts=posts,
            order_key=order_key,
            order_dir=order_dir
        )

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('akamatsu/dashboard/blog/ghost_index.html')

@bp_dashboard.route('/blog/new', methods=['GET', 'POST'])
@roles_required(['admin', 'blogger', 'superblogger'])
def blog_create():
    """Show the form for creating a new post."""
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post()
        form.populate_obj(new_post)

        # Add tags
        if form.tag_list.data:
            new_post.tag_names = set(
                [n.strip() for n in form.tag_list.data.split(',')]
            )

        if form.author_name.data:
            author = (
                User.query
                .filter_by(username=form.author_name.data).first()
            )

            if author:
                # Assign author ID to the post
                new_post.author_id = author.id

        else:
            # Set to current user by default
            new_post.author_id = current_user.id

        try:
            correct = True
            db.session.add(new_post)
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
                    'akamatsu/dashboard/blog/edit.html',
                    mode='create',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg
                )


        # Post saved return to index
        return redirect(url_for('dashboard.blog_index'))

    return render_template(
        'akamatsu/dashboard/blog/edit.html',
        mode='create',
        form=form
    )

@bp_dashboard.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@roles_required(['admin', 'blogger', 'superblogger'])
def blog_edit(post_id):
    """Show the form for editing an existing post.

    Arguments:
        post_id (int): Unique ID of the post to edit.
    """
    post = Post.query.filter_by(id=post_id).first()

    # Check existence
    if not post:
        return render_template(
            'akamatsu/dashboard/blog/edit.html',
            mode='edit',
            status='error',
            errmsg='The post does not exist'
        )

    # Check permissions
    if current_user.has_role('blogger') and post.author_id != current_user.id:
        return render_template(
            'akamatsu/dashboard/blog/edit.html',
            mode='edit',
            status='error',
            errmsg='You do not have the required permissions to edit the post'
        )


    form = PostForm(obj=post)

    # Get tags
    form.tag_list.data = form.tag_list.data or ','.join(post.tag_names)

    if form.validate_on_submit():
        # Try to find post author
        if form.author_name.data:
            author = (
                User.query
                .filter_by(username=form.author_name.data).first()
            )
        else:
            author = None

        # Check model can be saved
        form.populate_obj(post)

        # Add tags
        if form.tag_list.data:
            post.tag_names = set(
                [n.strip() for n in form.tag_list.data.split(',')]
            )

        # Set new author
        if author:
            # Assign author ID to the post
            post.author_id = author.id

        else:
            # Set to null
            post.author_id = None


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
                    'akamatsu/dashboard/blog/edit.html',
                    mode='edit',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg,
                    post_id=post_id
                )


        # Post saved, remain in the edition view
        return render_template(
            'akamatsu/dashboard/blog/edit.html',
            mode='edit',
            status='saved',
            form=form,
            post_id=post_id
        )

    # Get author name
    if post.author:
        form.author_name.data = form.author_name.data or post.author.username

    return render_template(
        'akamatsu/dashboard/blog/edit.html',
        mode='edit',
        status='edit',
        form=form,
        post_id=post_id
    )

@bp_dashboard.route('/blog/delete/<int:post_id>', methods=['GET', 'POST'])
@roles_required(['admin', 'blogger', 'superblogger'])
def blog_delete(post_id):
    """Confirm deletion of a post.

    GET requests show a message to confirm and POST requests delete the post
    and redirect back to index.

    Arguments:
        post_id (int): Unique ID of the post to delete.
    """
    post = Post.query.filter_by(id=post_id).first()

    # Check existence
    if not post:
        return render_template(
            'akamatsu/dashboard/blog/delete.html',
            status='error',
            errmsg = 'The post does not exist' % post_id
        )

    # Check permissions
    if current_user.has_role('blogger') and post.author_id != current_user.id:
        return render_template(
            'akamatsu/dashboard/blog/delete.html',
            status='error',
            errmsg='You do not have the required permissions to delete the post'
        )

    if request.method == 'POST':
        # Delete post
        try:
            correct = True
            db.session.delete(post)
            db.session.commit()

        except SQLAlchemyError as e:
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
                    'akamatsu/dashboard/blog/delete.html',
                    status='error',
                    errmsg=errmsg
                )


        return render_template(
            'akamatsu/dashboard/blog/delete.html',
            status='deleted'
        )

    # Show confirmation
    return render_template(
        'akamatsu/dashboard/blog/delete.html',
        status='confirm',
        post=post
    )


def _sort_posts(args):
    """Sort posts according to the specified key and order.

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
        result = Post.title

    elif key == 'slug':
        # Order by slug
        result = Post.slug

    elif key == 'published':
        # Order by published state
        result = Post.is_published

    elif key == 'comments':
        # Order by comments state
        result = Post.comments_enabled

    elif key == 'ghost':
        # Order by ghosting URL
        result = Post.ghost

    else:
        # Order by date
        key = 'date'
        result = Post.timestamp


    # Ordering
    if order == 'asc':
        return key, order, result

    order = 'desc'
    return key, order, result.desc()
