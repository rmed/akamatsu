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

"""This file contains unauthenticated blog views."""

from akamatsu.models import Post, User
from akamatsu.util import render_theme

from flask import Blueprint, redirect, request, url_for
from flask_misaka import markdown
from werkzeug.contrib.atom import AtomFeed
from werkzeug.exceptions import NotFound

bp_blog = Blueprint('blog', __name__)


@bp_blog.route('/atom.xml')
def feed():
    """Return an atom feed for the blog."""
    feed = AtomFeed(
        'Recent Posts',
        feed_url=request.url,
        url=request.url_root)

    posts = (
        Post.query
        .filter_by(is_published=True, ghost='')
        .order_by(Post.timestamp.desc())
        .limit(15))

    for post in posts:
        feed.add(
            post.title, markdown(post.content),
            content_type='html',
            author=post.author.username,
            url=url_for('blog.show', slug=post.slug, _external=True),
            updated=post.timestamp)

    return feed.get_response()

@bp_blog.route('/')
@bp_blog.route('/<int:page>')
def index(page=1):
    """Show the list of published posts.

    Args:
        page (int): Listing page number to show.
    """
    posts = (
        Post.query
        .filter_by(is_published=True, ghost='')
        .order_by(Post.timestamp.desc())
        .paginate(page, 10, False))

    try:
        return render_theme('blog/index.html', posts=posts)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_theme('blog/index.html')

@bp_blog.route('/tag/<tag>')
@bp_blog.route('/tag/<tag>/<int:page>')
def tagged(tag, page=1):
    """Display posts tagged with the given tag.

    Args:
        tag (str): Tag name.
        page (int): Listing page number to show.
    """
    posts = (
        Post.query
        .filter(Post.tags.any(name=tag))
        .filter_by(is_published=True, ghost='')
        .order_by(Post.timestamp.desc())
        .paginate(page, 10, False))

    try:
        return render_theme('blog/tagged.html', posts=posts, tag=tag)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_theme('blog/tagged.html', tag=tag)

@bp_blog.route('/by/<user>')
@bp_blog.route('/by/<user>/<int:page>')
def by_user(user, page=1):
    """Display posts tagged with the given tag.

    Args:
        user (str): Username of the author.
        page (int): Listing page number to show.
    """
    author = (
        User.query
        .filter_by(username=user)).first()

    if author:
        posts = (
            Post.query
            .filter_by(author_id=author.id, is_published=True, ghost='')
            .order_by(Post.timestamp.desc())
            .paginate(page, 10, False))

    else:
        posts = None

    try:
        return render_theme('blog/by.html', posts=posts, user=user)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_theme('blog/by.html', user=user)

@bp_blog.route('/<slug>')
def show(slug):
    """Show the contents of a specific post.

    Args:
        slug (str): Slug of the post to show.
    """
    post = Post.query.filter_by(is_published=True, slug=slug).first_or_404()

    # Check ghost redirection
    if post.ghost:
        return redirect(url_for('blog.show', slug=post.ghost), 301)

    return render_theme('blog/show.html', post=post)
