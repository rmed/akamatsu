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

from flask import Blueprint, Response, abort, current_app, redirect, \
        render_template, request, url_for
from feedgen.feed import FeedGenerator
from sqlalchemy import or_
from werkzeug.exceptions import NotFound

import pytz

from akamatsu import md as markdown
from akamatsu.models import Post, Role, User, user_posts, user_roles


bp_blog = Blueprint('blog', __name__)


@bp_blog.route('/_rss')
def feed():
    """Generate a RSS feed for the blog."""
    fg = FeedGenerator()

    fg.id(url_for('blog.index', _external=True))
    fg.title('{} feed'.format(current_app.config['SITENAME']))
    fg.description('{} feed'.format(current_app.config['SITENAME']))
    fg.author({'name': current_app.config['SITENAME']})
    fg.link(href=url_for('blog.index', _external=True), rel='alternate')
    # fg.logo('http://ex.com/logo.jpg')
    fg.link(href=url_for('blog.feed', _external=True), rel='self')
    fg.language(current_app.config['LOCALE'])

    # Add contributors
    users = (
        User.query
        .join(user_roles)
        .join(Role)
        .filter(User.is_active == True)
        .filter(
            or_(
                Role.name == 'administrator',
                Role.name == 'blogger'
            )
        )
    )

    contributors = []

    for user in users:
        name = user.username

        if user.first_name and user.last_name:
            name = '{} {}'.format(user.first_name, user.last_name)

        contributors.append({
            'name': name,
            #'email': user.email
        })

    fg.contributor = contributors

    # Add entries
    posts = (
        Post.query
        .filter_by(is_published=True)
        .filter_by(ghosted_id=None)
        .order_by(Post.last_updated.desc())
        .limit(15)
    )

    for post in posts:
        # Unicode conversion is needed for the content
        entry = fg.add_entry()

        entry.id(url_for('blog.show', slug=post.slug, _external=True))
        entry.link(href=url_for('blog.show', slug=post.slug, _external=True))
        entry.title(post.title)
        entry.updated(pytz.utc.localize(post.last_updated))
        entry.description(
            description=markdown.render(
                post.content.split('<!--aka-break-->')[0]
            ).unescape(),
            isSummary=True
        )
        entry.content(
            content=markdown.render(post.content).unescape(),
            type='html'
        )

        authors = []

        for author in post.authors:
            name = author.username

            if author.first_name and author.last_name:
                name = '{} {}'.format(author.first_name, author.last_name)

            contributors.append({
                'name': name,
                #'email': author.email
            })

    return Response(fg.rss_str(), mimetype='text/xml')


@bp_blog.route('/')
def index():
    """Show the list of published posts.

    Args:
        page (int): Page to show.
    """
    page = request.args.get('page', 1, int)

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


@bp_blog.route('/tagged/<tag>')
def tagged(tag):
    """Display posts tagged with the given tag.

    Args:
        tag (str): Tag name.
        page (int): Page to show.
    """
    page = request.args.get('page', 1, int)

    posts = (
        Post.query
        .filter(Post.tags.any(name=tag))
        .filter_by(is_published=True)
        .filter_by(ghosted_id=None)
        .order_by(Post.last_updated.desc())
        .paginate(page, current_app.config['PAGE_ITEMS'], False)
    )

    try:
        return render_template('blog/index.html', posts=posts, tag=tag)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('blog/index.html', tag=tag)


@bp_blog.route('/by/<username>')
def by_user(username):
    """Display posts written by the given user.

    This includes collaboration posts.

    Args:
        username (str): Username of the author.
        page (int): Page to show.
    """
    page = request.args.get('page', 1, int)

    posts = (
        Post.query
        .join(user_posts)
        .join(User)
        .filter(Post.is_published==True)
        .filter(Post.ghosted_id==None)
        .filter(User.username==username)
        .order_by(Post.last_updated.desc())
        .paginate(page, current_app.config['PAGE_ITEMS'], False)
    )

    try:
        return render_template('blog/index.html', posts=posts, username=username)

    except NotFound:
        # Show a 'no posts found' notice instead of a 404 error
        return render_template('blog/index.html', username=username)


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
