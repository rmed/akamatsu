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

"""This file contains SQLAlchemy model declarations."""

import datetime

import slugify

from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

from akamatsu import db, hashids_hasher


# Intermediate user-role table
user_roles = db.Table(
    'user_roles',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id', name='fk_user_roles_user'),
        primary_key=True
    ),
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey('roles.id', name='fk_user_roles_role'),
        primary_key=True
    )
)


# Intermediate user-post table
user_posts = db.Table(
    'user_posts',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id', name='fk_user_posts_user'),
        primary_key=True
    ),
    db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('posts.id', name='fk_user_posts_post'),
        primary_key=True
    )
)


# Intermediate post-tag table
post_tags = db.Table(
    'post_tags',
    db.Column(
        'post_id',
        db.Integer,
        db.ForeignKey('posts.id', name='fk_post_tags_post'),
        primary_key=True
    ),
    db.Column(
        'tag_id',
        db.Integer,
        db.ForeignKey('tags.id', name='fk_post_tags_tag'),
        primary_key=True
    )
)


class BaseModel(db.Model):
    """Base class used to implement common methods."""
    __abstract__ = True

    @property
    def hashid(self):
        """Obtain the HashId token on the fly."""
        return hashids_hasher.encode(self.id)

    @classmethod
    def exists(cls, id):
        """Check whether an instance exists.

        Returns:
            Boolean indicating if the instance exists.
        """
        return cls.query.filter_by(id=id).scalar()

    @classmethod
    def get_by_id(cls, id):
        """Get instance by id.

        Returns:
            Instance or `None` if not found.
        """
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_hashid(cls, token):
        """Get instance by HashId token.

        Returns:
            Instance or `None` if not found.
        """
        instance_id = hashids_hasher.decode(token)

        if not instance_id:
            return None

        return cls.query.filter_by(id=instance_id[0]).first()

    def update(self, **kwargs):
        """Update instance attributes from dictionary.

        Key and value validation should be performed beforehand!
        """
        for k, v in kwargs.items():
            setattr(self, k, v)


# CMS models
class FileUpload(BaseModel):
    """Model for static file uploads.

    Attributes:
        id (int): Unique ID of the record.
        path (str): Path to the file relative to the uploads directory.
        description (str): Optional description of the file.
        uploaded (datetime): UTC datetime in which the file was uploaded.
    """
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)

    path = db.Column(db.String(512), nullable=False, unique=True)
    description = db.Column(db.String(256), nullable=True)
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow()
    )


class Page(BaseModel):
    """Model for dynamic pages.

    Pages may be written in markdown (default) or in html. Security should
    be taken into consideration when writing html.

    The `<head>` can be extended (e.g. to add some custom JS scripts) when
    writing pages in html.

    The flag `is_root` determines whether the page is the root of the website
    ('/'), there can only be one. If there are more records with this tag,
    the first one found will be used.

    Pages can "ghost" other pages, meaning that accessing a ghost page will
    redirect to the page being ghosted.

    Attributes:
        id (int): Unique page ID.
        ghosted_id (int): ID of the page the browser will be redirected to
            when accessing this page. If set to `None`, this page will not be
            a ghost page.
        title (str): Title of the page.
        mini (str): Optional text to show at the top of the page.
        route (str): Route to this page. Must be unique.
        custom_head (str): Add custom html to the `<head>` of the template.
        content (str): Main content of the page. This can be written in markdown
            or html.
        is_published (bool): Whether the page is published.
        comments_enabled (bool): Whether comments are enabled for this page.
        last_updated (datetime): UTC datetime in which the page was last edited.
    """
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)

    ghosted_id = db.Column(
        db.Integer,
        db.ForeignKey('pages.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True
    )
    title = db.Column(db.String(255), nullable=False)
    mini = db.Column(db.String(50), nullable=False)
    route = db.Column(db.String(512), nullable=False, unique=True)
    custom_head = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    comments_enabled = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime)

    # Relationships
    ghosted = db.relationship(
        'Page',
        primaryjoin='Page.ghosted_id == Page.id',
    )


class Post(BaseModel):
    """Model for blog posts.

    Posts are written in markdown.

    Attributes:
        id (int): ID of the record.
        ghosted_id (int): ID of the post the browser will be redirected to
            when accessing this page. If set to `None`, this post will not
            be a ghost post.
        title (str): Title of the post.
        slug (str): Slug of the post. Can be automatically generated.
        is_published (bool): Whether the post is published.
        comments_enabled (bool): Whether comments are enabled for this post.
        last_updated (datetime): UTC datetime in which the post was last edited.
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)

    ghosted_id = db.Column(
        db.Integer,
        db.ForeignKey('posts.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True
    )
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(512), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    comments_enabled = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime)

    # Relationships
    ghosted = db.relationship(
        'Post',
        primaryjoin='Post.ghosted_id == Post.id'
    )

    authors = db.relationship(
        'User', secondary='user_posts',
        backref=db.backref('posts', lazy='dynamic'),
        cascade='delete, save-update', collection_class=set
    )

    tags = db.relationship(
        'Tag', secondary='post_tags',
        backref=db.backref('posts', lazy='dynamic'),
        cascade='delete, save-update', collection_class=set
    )

    # Proxies
    tab_names = association_proxy(
        'tags',
        'name',
        creator=lambda n: Tag.get_or_new(n)
    )


class Tag(db.Model):
    """Post taggings.

    Attributes:
        id (int): Unique ID of the tag.
        name (str): Unique name of the tag.
    """
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    @classmethod
    def get_or_new(self, name):
        """Obtain an already existing tag or create a new one.

        Args:
            name (str): Unique name for the tag.

        Returns:
            `Tag` instance or `None`.
        """
        tag = Tag.query.filter_by(name=name).first()

        if tag:
            return tag

        return Tag(name=name)


# Authentication/Authorization models
class Role(BaseModel):
    """Model for defining roles.

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
        return Role.query.filter_by(name=name).first()


class User(BaseModel, UserMixin):
    """User model.

    Attributes:
        username (str): Unique username.
        password (str): Password hash.
        reset_password_token (str): Token used to reset user password.
        email (str): Email of the user.
        is_active (bool): Whether the user is active in the application.
        notify_login (bool): Whether the user should be notified by mail
            each time a new session is started.
        personal_bio (str): Personal bio in markdown.
        roles (set(Role)): Roles assigned to the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    reset_password_token = db.Column(db.String(100), nullable=True)
    reset_expiration = db.Column(db.DateTime(), nullable=True)

    # Email information
    email = db.Column(db.String(255), nullable=False, unique=True)

    # User information
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')

    # Additional attributes
    personal_bio = db.Column(db.String(1024), nullable=True)
    notify_login = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    roles = db.relationship(
        'Role', secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'),
        cascade='delete, save-update', collection_class=set
    )

    # Proxies
    role_names = association_proxy(
        'roles',
        'name',
        creator=lambda n: Role.get_role(n)
    )

    @classmethod
    def get_by_username(self, username):
        """Obtain an already existing user by username.

        Args:
            username (str): Unique username of the user

        Returns:
            User instance or `None` if not found.
        """
        return User.query.filter_by(username=username).first()


# Events
@event.listens_for(Post, 'before_insert')
def before_post_insert(mapper, connection, post):
    """Perform actions before a post is first created.

    These include:
        - Slugify the title of the post if not present
    """
    if not post.slug:
        post.slug = slugify.slugify(post.title, to_lower=True, max_length=512)
