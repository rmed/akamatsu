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

"""This file contains unauthenticated blog views."""

from flask import Blueprint, abort, current_app, redirect, render_template, \
        request, url_for
from werkzeug.contrib.atom import AtomFeed
from werkzeug.exceptions import NotFound

from akamatsu import md as markdown
from akamatsu.models import Post, User


bp_blog = Blueprint('blog', __name__)


@bp_blog.route('/atom.xml')
def feed():
    """Generate an atom feed for the blog."""
    feed = AtomFeed(
        '{}: Recent posts'.format(current_app.config.get('SITENAME', 'akamatsu')),
        feed_url=request.url,
        url=request.url_root
    )

    posts = (
        Post.query
        .filter_by(is_published=True)
        .filter_by(ghosted_id=None)
        .order_by(Post.last_updated.desc())
        .limit(15)
    )

    for post in posts:
        # Unicode conversion is needed for the content
        feed.add(
            post.title,
            markdown.render(post.content).unescape(),
            content_type='html',
            author=[a.username for a in post.authors],
            url=url_for('blog.show', slug=post.slog, _external=True),
            updated=post.last_updated
        )

    return feed.get_response()


@bp_blog.route('/')
@bp_blog.route('/<int:page>')
def index(page=1):
    """Show the list of published posts.

    Args:
        page (int): Page to show.
    """
    posts = (
        Post.query
        .filter_by(is_published=True)
        .filter_by(ghosted_id=None)
        .order_by(Post.last_updated.desc())
        .paginate(page, current_app.config['PAGE_ITEMS'], False)
    )

    try:
        return render_template('blog/index.html', posts=posts)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('blog/index.html')


@bp_blog.route('/tag/<tag>')
@bp_blog.route('/tag/<tag>/<int:page>')
def tagged(tag, page=1):
    """Display posts tagged with the given tag.

    Args:
        tag (str): Tag name.
        page (int): Page to show.
    """
    posts = (
        Post.query
        .filter(Post.tags.any(name=tag))
        .filter_by(is_published=True)
        .filter_by(ghosted_id=None)
        .order_by(Post.last_updated.desc())
        .paginate(page, current_app.config['PAGE_ITEMS'], False)
    )

    try:
        return render_template('blog/tagged.html', posts=posts)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('blog/tagged.html')


@bp_blog.route('/by/<username>')
@bp_blog.route('/by/<username>/<int:page>')
def by_user(username, page=1):
    """Display posts written by the given user.

    This includes collaboration posts.

    Args:
        username (str): Username of the author.
        page (int): Page to show.
    """
    posts = (
        Post.query
        .join(User)
        .filter(Post.is_published==True)
        .filter(Post.ghosted_id==None)
        .filter(User.username==username)
        .order_by(Post.last_updated.desc())
        .paginate(page, current_app.config['PAGE_ITEMS'], False)
    )

    try:
        return render_template('blog/by_user.html', posts=posts)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('blog/by_user.html')


@bp_blog.route('/<slug>')
def show(slug):
    """Show the contents of a specific post.

    Args:
        slug (str): Slug of the post to show.
    """
    post = (
        Post.query
        .filter_by(is_published=True)
        .filter_by(slug=slug)
    ).first_or_404()

    # Check ghost redirection
    if post.ghosted_id is not None:
        if post.ghosted_id == post.id:
            # Prevent loops
            abort(404)

        # Only published posts are allowed
        ghosted = (
            Post.query
            .filter_by(id=post.ghosted_id)
            .filter_by(is_published=True)
        ).first_or_404()

        return redirect(url_for('blog.show', slug=ghosted.slug))

    return render_template('blog/show.html', post=post)
