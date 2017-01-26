# -*- coding: utf-8 -*-
#
# Akamatsu CMS
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

"""This file contains SQLAlchemy model declarations."""

from akamatsu import db

from flask_user import UserMixin
from flask_waffleconf import WaffleMixin
from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

import datetime
import slugify


# Additional relationship tables

# Post taggings
post_tags = db.Table('post_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)


# CMS models
class Post(db.Model):
    """Model representing blog posts.

    Posts are written in markdown.

    Attributes:
        id (int): ID of the record.
        title (str): Title of the post.
        content (str): Content of the post (in markdown).
        ghost (str): If present, the route shown in this attribute will
            be used when accessing to this post.
        slug (str): Slug of the post, automatically generated.
        is_published (bool): Whether or not the post has been published.
        comments_enabled (bool): Whether or not comments should be shown.
        timestamp (date): Date in which the post was created/edited.

        author (User): Author of the post.
        tags (Tag): List of tags of the post.
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    ghost = db.Column(db.String(512), nullable=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    comments_enabled = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime)

    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship(
        'User',
        primaryjoin='Post.author_id == User.id',
       backref=db.backref('posts', lazy='dynamic'))

    tags = db.relationship(
        'Tag', secondary=post_tags,
        backref=db.backref('posts', lazy='dynamic'),
        cascade='delete, save-update', collection_class=set)

    # Proxies
    tag_names = association_proxy(
            'tags', 'name', creator=lambda n: Tag.get_or_new(n))

class Page(db.Model):
    """Model representing dynamic pages.

    Pages may be written in markdown (default) or in html. Security should
    be taken into consideration when writing html.

    The `<head>` can be extended (e.g. to add some custom JS scripts) when
    writing pages in html.

    The flag `is_root` determines whether the page is the root of the
    website ('/'), there can be only one. If there are more records with
    this tag, the first one found will be used.

    Attributes:
        id (int): Unique page ID.
        title (str): Title of the page.
        mini (str): Optional text to show at the top of the page.
        content (str): Main content of the page. This can be written in
            markdown or html.
        custom_head (str): Add custom html to the ``<head>`` of the template.
        ghost (str): If present, the route shown in this attribute will
            be used when accessing to this page.
        base_route (str): Base route of the page. This will be appended to
            the ``route`` attribute with ``slug`` to determine route needed to
            access the page.
        slug (str): Slug of the page, automatically generated.
        route (str): Modified automatically. Route to this page formed by the
            ``base_route`` and ``slug`` attributes.
        is_root (bool): Whether this page is the one accessed through '/'.
        is_published (bool): Whether this page is published or not.
        comments_enabled (bool): Whether or not to show comments for the page.
        timestamp (date): Date in which the page was created/edited.
    """
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    mini = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=False)
    custom_head = db.Column(db.Text, nullable=True)
    ghost = db.Column(db.String(512), nullable=True)
    base_route = db.Column(db.String(255), nullable=False, default='/')
    slug = db.Column(db.String(255), unique=False, nullable=False)
    route = db.Column(db.String(512), unique=True, nullable=False)
    is_root = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    comments_enabled = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime)


class Tag(db.Model):
    """Post taggings.

    Attributes:
        id (int): Unique ID of the tag.
        name (str): Unique name of the tag.
    """
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_or_new(self, name):
        """Obtain an already existing tag or create a new one.

        Args:
            name (str): Unique name of the tag.

        Returns:
            Tag instance.
        """
        tag = Tag.query.filter_by(name=name).first()

        if tag:
            return tag

        return Tag(name)

# Flask-User models
class Role(db.Model):
    """Flask-User model for user roles.

    Generally, only three roles exist for this app:

        admin: total control (edits users, settings, pages, posts)
        editor: can edit pages
        blogger: can publish posts (and edit their own)

    Attributes:
        id (int): Unique ID of the role.
        name (str): Unique name of the role.
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    @classmethod
    def get_role(self, name):
        """Obtain an already existing role by name.

        Args:
            name (str): Unique name of the role.

        Returns:
            Role instance or None if not found.
        """
        role = Role.query.filter_by(name=name).first()

        return role


class User(db.Model, UserMixin):
    """Flask-User model for users.

    Includes additional attributes used for CMS purposes.

    Attributes:
        notify_login (bool): Whether or not the user should be notified by
            mail everytime a new session is started.
        personal_bio (str): Personal BIO in markdown.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

    # Email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime)

    # User information
    is_enabled = db.Column(db.Boolean, nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')

    # Additional attributes
    personal_bio = db.Column(db.String(1024), nullable=True, default='')
    notify_login = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    roles = db.relationship(
        'Role', secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'),
        cascade='delete, save-update', collection_class=set)

    # Proxies
    role_names = association_proxy(
            'roles', 'name', creator=lambda n: Role.get_role(n))

    def is_active(self):
        return self.is_enabled


    @classmethod
    def get_user(self, username):
        """Obtain an already existing user by username.

        Args:
            username (str): Unique username of the user

        Returns:
            User instance or None if not found.
        """
        user = User.query.filter_by(username=username).first()

        return user


class UserRoles(db.Model):
    """Flask-User model for user-role relations."""
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer,
            db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    role_id = db.Column(db.Integer,
            db.ForeignKey('roles.id', onupdate='CASCADE', ondelete='CASCADE'))


# Flask-WaffleConf
class WaffleModel(db.Model, WaffleMixin):
    """Flask-WaffleConf model for storing variables."""
    __tablename__ = 'waffleconfs'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)


# File uploads
class FileUpload(db.Model):
    """Model representing a static file upload.

    Attributes:
        id (int): Unique ID of the model.
        path (str): Path to the file relative to the uploads directory.
        description (str): Optional description of the file.
        timestamp (date): Date in which the file was uploaded.
    """
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(512), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now()
    )


# Events

@event.listens_for(Page, 'before_insert')
def before_page_insert(mapper, connection, page):
    """Perform actions before a page is first created.

    These include:
        - Slugify the title of the page if no slug is provided.
        - Set the route of the page.
    """
    # Slug
    if not page.slug:
        page.slug = slugify.slugify(page.title, to_lower=True, max_length=255)

    # Route
    if page.is_root:
        # Root page
        page.route = '/'

    else:
        slash = '' if page.base_route.endswith('/') else '/'
        page.route = page.base_route + slash + page.slug

@event.listens_for(Page, 'before_update')
def before_page_update(mapper, connection, page):
    """Perform actions before updating a page.

    These include:
        - Set the route of the page.
    """
    if page.is_root:
        # Root page
        page.route = '/'

    else:
        slash = '' if page.base_route.endswith('/') else '/'
        page.route = page.base_route + slash + page.slug

@event.listens_for(Post, 'before_insert')
def before_post_insert(mapper, connection, post):
    """Perform actions before a post is first created.

    These include:
        - Slugify the title of the post.
    """
    if not post.slug:
        post.slug = slugify.slugify(post.title, to_lower=True, max_length=255)
