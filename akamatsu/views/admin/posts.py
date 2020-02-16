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

from urllib.parse import unquote

from flask import abort, current_app, flash, jsonify, redirect, \
        render_template, request, url_for
from flask_babel import _
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from wtforms import ValidationError

from akamatsu import db
from akamatsu.models import user_posts, Post, User
from akamatsu.views.admin import bp_admin
from akamatsu.forms import PostForm
from akamatsu.util import allowed_roles, datetime_to_utc, is_ajax, is_safe_url, \
        utc_to_local_tz


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

    posts, sort_key, order_dir = _sort_posts(posts, sort_key, order_dir)


    if current_user.has_role('blogger'):
        posts = (
            posts
            .join(user_posts)
            .join(User)
            .filter(User.id == current_user.id)
        )

    posts = posts.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if is_ajax():
        # AJAX request
        return render_template(
            'admin/posts/partials/posts_page.html',
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

    posts, sort_key, order_dir = _sort_posts(posts, sort_key, order_dir)

    if current_user.has_role('blogger'):
        posts = (
            posts
            .join(user_posts)
            .join(User)
            .filter(User.id == current_user.id)
        )

    posts = posts.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if is_ajax():
        # AJAX request
        return render_template(
            'admin/posts/partials/ghosts_page.html',
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
            # Need to manually rollback here
            db.session.rollback()
            form.slug.errors.append(_('Post slug is already in use'))

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
    """Edit an existing post.

    Administrators can edit any post, while regular users can only edit
    posts in which they have participated.

    Args:
        hashid (str): HashID of the post.
    """
    post = Post.get_by_hashid(hashid)

    if not post:
        flash(_('Could not find post'), 'error')

        return redirect(url_for('admin.post_index'))

    if not current_user.has_role('administrator'):
        if current_user not in post.authors:
            flash(_('You cannot edit that post'), 'warning')

            return redirect(url_for('admin.post_index'))

    form = PostForm(obj=post)

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

        form.populate_obj(post)

        # Adjust timezone
        post.last_updated = datetime_to_utc(post.last_updated)

        # Current user is always an author
        if current_user not in post.authors:
            post.authors.append(current_user)

        # Add tags
        if form.tag_list.data:
            post.tag_names = set(
                n.strip() for n in form.tag_list.data.split(',')
            )

        try:
            correct = True
            db.session.commit()

            flash(_('Post updated correctly'), 'success')

            return redirect(
                url_for('admin.edit_post', hashid=hashid)
            )

        except IntegrityError:
            # Slug already exists
            # Need to manually rollback here
            db.session.rollback()
            form.slug.errors.append(_('Post slug is already in use'))

            return render_template('admin/posts/edit.html', form=form, post=post)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to update post, contact an administrator'), 'error')

            return render_template('admin/posts/edit.html', form=form, post=post)

        finally:
            if not correct:
                db.session.rollback()


    # First load checks
    if request.method == 'GET':
        # Date
        form.last_updated.data = utc_to_local_tz(form.last_updated.data)

        # Tags
        form.tag_list.data = ','.join(post.tag_names)

    return render_template('admin/posts/edit.html', form=form, post=post)


@bp_admin.route('/posts/<hashid>/delete', methods=['GET', 'POST'])
@allowed_roles('administrator', 'blogger')
def delete_post(hashid):
    """Delete a post.

    Administrators can delete any post, while regular users can only delete
    posts in which they have participated.

    Usual flow is by calling this endpoint from AJAX (button in post listing).

    If the query parameter "ref" is set, the browser will be redirected to that
    URL after deletion (if it is safe).

    Args:
        hashid (str): HashID of the post.
    """
    post = Post.get_by_hashid(hashid)

    if not post:
        flash(_('Could not find post'), 'error')

        return redirect(url_for('admin.post_index'))

    if not current_user.has_role('administrator'):
        if current_user not in post.authors:
            flash(_('You cannot delete that post'), 'warning')

            return redirect(url_for('admin.post_index'))

    if request.method == 'POST':
        # Delete post
        ref = unquote(request.args.get('ref', ''))

        try:
            correct = True
            db.session.delete(post)
            db.session.commit()

            flash(_('Post "%(title)s" deleted', title=post.title), 'success')

            # Redirect user
            if ref and is_safe_url(ref):
                # Provided as query parameter
                if is_ajax():
                    return jsonify({'redirect': ref}), 200

                return redirect(ref)

            # Default to index
            dest = 'admin.post_ghosts' if post.ghosted_id else 'admin.post_index'

            if is_ajax():
                return jsonify({'redirect': url_for(dest)}), 200

            return redirect(url_for(dest))

        except ValidationError:
            # CSRF invalid
            correct = False
            current_app.logger.exception('Failed to delete post')

            flash(_('Failed to delete post, invalid CSRF token received'), 'error')

        except Exception:
            # Catch anything unknown
            correct = False
            current_app.logger.exception('Failed to delete post')

            flash(_('Failed to delete post, unknown error encountered'), 'error')

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                # Check AJAX
                if is_ajax():
                    abort(400)

                return redirect(
                    url_for('admin.edit_post', hashid=hashid)
                )

    # Check AJAX
    if is_ajax():
        return render_template(
            'admin/posts/partials/delete_modal.html',
            post=post,
            ref=request.args.get('ref', '')
        )

    return render_template(
        'admin/posts/delete.html',
        post=post
    )


def _sort_posts(query, key, order):
    """Sort posts according to the specified key and order.

    Args:
        query: Original query to order.
        key (str): Key to order by.
        order (str): Order direction ("asc" or "desc").

    Returns:
        Tuple with ordered query, key, order.
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
            return query.order_by(alias.title), key, order

        order = 'desc'
        return query.order_by(alias.title.desc()), key, order

    elif key == 'date':
        # Order by date
        ordering = Post.last_updated

    else:
        # Order by date and don't set ordering
        return query.order_by(Post.last_updated.desc()), None, None

    # Ordering
    if order == 'asc':
        return query.order_by(ordering), key, order

    order = 'desc'
    return query.order_by(ordering.desc()), key, order
