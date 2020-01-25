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

"""This module contains post views."""

import slugify

from flask import current_app, flash, redirect, render_template, request, \
        url_for
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from akamatsu import db
from akamatsu.models import user_posts, Post, User
from akamatsu.views.admin import bp_admin
from akamatsu.forms import PostForm
from akamatsu.util import allowed_roles, datetime_to_utc


@bp_admin.route('/posts')
@allowed_roles('administrator', 'blogger')
def post_index():
    """Display a paginated list of posts.

    Only active posts are shown (not ghosts).

    If this endpoint is called from AJAX, only the requested page contents
    are returned.
    """
    page = request.args.get('page', 1, int)
    sort_key = request.args.get('sort')
    order_dir = request.args.get('order')

    # Users can only see posts in which they have participated
    # (unless they are administrators)
    posts = (
        Post.query
        .filter(Post.ghosted_id == None)
    )

    sort_key, order_dir, posts = _sort_posts(posts, sort_key, order_dir)


    if current_user.has_role('blogger'):
        posts = (
            posts
            .join(user_posts)
            .join(User)
            .filter(User.id == current_user.id)
        )

    posts = posts.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if request.is_xhr:
        # AJAX request
        return render_template(
            'admin/posts/partial/posts_page.html',
            posts=posts,
            sort_key=sort_key,
            order_dir=order_dir
        )

    return render_template(
        'admin/posts/index.html',
        posts=posts,
        sort_key=sort_key,
        order_dir=order_dir
    )


@bp_admin.route('/post-ghosts')
@allowed_roles('administrator', 'blogger')
def post_ghosts():
    """Display a paginated list of post ghosts.

    If this endpoint is called from AJAX, only the requested page contents
    are returned.
    """
    page = request.args.get('page', 1, int)
    sort_key = request.args.get('sort')
    order_dir = request.args.get('order')

    # Users can only see posts in which they have participated
    # (unless they are administrators)
    posts = (
        Post.query
        .filter(Post.ghosted_id != None)
    )

    sort_key, order_dir, posts = _sort_posts(posts, sort_key, order_dir)

    if current_user.has_role('blogger'):
        posts = (
            posts
            .join(user_posts)
            .join(User)
            .filter(User.id == current_user.id)
        )

    posts = posts.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if request.is_xhr:
        # AJAX request
        return render_template(
            'admin/posts/partial/ghosts_page.html',
            posts=posts,
            sort_key=sort_key,
            order_dir=order_dir
        )

    return render_template(
        'admin/posts/ghost_index.html',
        posts=posts,
        sort_key=sort_key,
        order_dir=order_dir
    )


@bp_admin.route('/posts/new', methods=['GET', 'POST'])
@allowed_roles('administrator', 'blogger')
def new_post():
    """Create a new post."""
    form = PostForm()

    # Posts available to ghost
    if current_user.has_role('administrator'):
        # All posts
        form.ghosted.query = (
            Post.query
            .filter(Post.ghosted_id == None)
            .order_by(Post.title)
        )

    elif current_user.has_role('blogger'):
        # Own posts
        form.ghosted.query = (
            Post.query
            .join(user_posts)
            .join(User)
            .filter(Post.ghosted_id == None)
            .filter(User.id == current_user.id)
        )

    # Authors
    form.authors.query = (
        User.query
        .filter_by(is_active=True)
        .filter(User.id != current_user.id)
        .order_by(User.username)
    )

    if form.validate_on_submit():
        # Slug
        if not form.slug.data:
            form.slug.data = slugify.slugify(
                form.title.data,
                to_lower=True,
                max_length=512
        )

        new_post = Post()
        form.populate_obj(new_post)

        # Adjust timezone
        new_post.last_updated = datetime_to_utc(new_post.last_updated)

        print(new_post.last_updated)

        # Current user is always an author
        if current_user not in new_post.authors:
            new_post.authors.append(current_user)

        # Add tags
        if form.tag_list.data:
            new_post.tag_names = set(
                n.strip() for n in form.tag_list.data.split(',')
            )

        try:
            correct = True
            db.session.add(new_post)
            db.session.commit()

            flash(_('New post created correctly'), 'success')

            return redirect(url_for('admin.post_index'))

        except IntegrityError:
            # Slug already exists
            correct = False
            form.slug.email.append(_('Post slug is already in use'))

            return render_template('admin/posts/edit.html', form=form)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to create post, contact an administrator'), 'error')

            return render_template('admin/posts/edit.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('admin/posts/edit.html', form=form)


@bp_admin.route('/posts/<hashid>', methods=['GET', 'POST'])
@allowed_roles('administrator', 'blogger')
def edit_post(hashid):
    """Create a new post."""
    pass


def _sort_posts(query, key, order):
    """Sort posts according to the specified key and order.

    Args:
        query: Original query to order.
        key (str): Key to order by.
        order (str): Order direction ("asc" or "desc").

    Returns:
        Tuple with key, order and ordered query.
    """
    ordering = None

    if key == 'title':
        # Order by title
        ordering = Post.title

    elif key == 'slug':
        # Order by slug
        ordering = Post.slug

    elif key == 'published':
        # Order by published state
        ordering = Post.is_published

    elif key == 'comments':
        # Order by comments state
        ordering = Post.comments_enabled

    elif key == 'ghost':
        # Order by ghosted title
        alias = aliased(Post)
        query = (
            query
            .join(alias, Post.ghosted)
        )

        if order == 'asc':
            return key, order, query.order_by(alias.title)

        order = 'desc'
        return key, order, query.order_by(alias.title.desc())

    elif key == 'date':
        # Order by date
        ordering = Post.last_updated

    else:
        # Order by date and don't set ordering
        return None, None, query.order_by(Post.last_updated.desc())

    # Ordering
    if order == 'asc':
        return key, order, query.order_by(ordering)

    order = 'desc'
    return key, order, query.order_by(ordering.desc())
