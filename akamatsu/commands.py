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

"""This file contains custom CLI commands."""

import datetime
import json
import os

from flask.cli import FlaskGroup

from akamatsu import db, crypto_manager, init_app
from akamatsu.models import FileUpload, Page, Post, Role, User

import click


def init_wrapper(info):
    """Wrapper for the application initialization function."""
    return init_app()


@click.group(cls=FlaskGroup, create_app=init_wrapper)
def cli():
    """Management script."""
    pass


# Begin user commands
@cli.group()
def user():
    """User related commands."""
    pass


@user.command()
@click.argument('username')
@click.argument('role')
def addrole(username, role):
    """Add a role to a given user.

    \b
    Args:
        username: the username to add the role to
        role: role name
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    if role in user.role_names:
        click.echo('User already has that role')
        return


    role_exists = Role.query.filter_by(name=role).scalar()

    if not role_exists:
        click.echo('Role does not exist')
        return

    # Update roles
    roles = [r for r in user.role_names]
    roles.append(role)

    user.role_names = set(roles)

    try:
        correct = True
        db.session.commit()

        click.echo('Roles updated')

    except Exception as e:
        # Catch anything unknown
        correct = False

        click.echo('Error updating roles')
        click.echo(e)


    finally:
        if not correct:
            # Cleanup
            db.session.rollback()


@user.command()
@click.option('--username', help='username (must be unique)', prompt=True)
@click.option('--email', help='email (must be unique)', prompt=True)
@click.option('--password', help='password', prompt=True, hide_input=True)
def create(username, email, password):
    """Add a new user to the database."""
    hashed_password = crypto_manager.hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        is_active=True,
        notify_login=False
    )

    try:
        correct = True
        db.session.add(new_user)
        db.session.commit()

        click.echo('New user created')

    except Exception as e:
        # Catch anything unknown
        correct = False

        click.echo(
            'Error creating user, make sure username and email are unique'
        )
        click.echo(e)

    finally:
        if not correct:
            # Cleanup
            db.session.rollback()


@user.command()
@click.argument('username')
def deactivate(username):
    """Deactivate a user account.

    \b
    Args:
        username: the username to disable
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    if not user.is_active:
        click.echo('User is already deactivated')
        return

    user.is_active = False

    try:
        correct = True
        db.session.commit()

        click.echo('User deactivated')

    except Exception as e:
        # Catch anything unknown
        correct = False

        click.echo('Error deactivating user')
        click.echo(e)

    finally:
        if not correct:
            # Cleanup
            db.session.rollback()


@user.command()
@click.argument('username')
def activate(username):
    """Activate a user account.

    \b
    Args:
        username: the username to enable
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    if user.is_active:
        click.echo('User is already active')
        return

    user.is_active = True

    try:
        correct = True
        db.session.commit()

        click.echo('User activated')

    except Exception as e:
        # Catch anything unknown
        correct = False

        click.echo('Error activating user')
        click.echo(e)

    finally:
        if not correct:
            # Cleanup
            db.session.rollback()


@user.command()
@click.argument('username')
@click.option('--password', help='password', prompt=True, hide_input=True)
def password(username, password):
    """Change the password of a user.

    \b
    Args:
        username: user to change password for
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    user.password = crypto_manager.hash(password)

    try:
        correct = True
        db.session.commit()

        click.echo('Password changed')

    except Exception as e:
        # Catch anything unknown
        correct = False

        click.echo('Failed to change password')
        click.echo(e)

    finally:
        if not correct:
            # Cleanup
            db.session.rollback()


@user.command()
@click.argument('username')
def roles(username):
    """Show roles of a given user.

    \b
    Args:
        username: the username to list roles for
    """
    user = User.get_by_username(username)

    if not user:
        click.echo('User does not exist')
        return

    roles = ', '.join(user.role_names) or 'No roles'

    click.echo('Roles of user "{}}": {}'.format(username, roles))


# Begin translation commands
@cli.group()
def translate():
    """Translation and localization commands."""
    pass


@translate.command()
def compile():
    """Compile all languages."""
    compile_cmd = (
        'pybabel compile '
        '-d akamatsu/translations'
    )

    if os.system(compile_cmd):
        raise RuntimeError('compile command failed')


@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    extract_cmd = (
        'pybabel extract '
        '-F babel.cfg '
        '-k "lazy_gettext _l" '
        '-o akamatsu/translations/messages.pot .'
    )

    init_cmd = (
        'pybabel init '
        '-i akamatsu/translations/messages.pot '
        '-d akamatsu/translations '
        '-l {}'
    )

    if os.system(extract_cmd):
        raise RuntimeError('extract command failed')

    if os.system(init_cmd.format(lang)):
        raise RuntimeError('init command failed')


@translate.command()
def update():
    """Update message catalog."""
    extract_cmd = (
        'pybabel extract '
        '-F babel.cfg '
        '-k "lazy_gettext _l" '
        '-o akamatsu/translations/messages.pot .'
    )

    update_cmd = (
        'pybabel update '
        '-i akamatsu/translations/messages.pot '
        '-d akamatsu/translations'
    )


    if os.system(extract_cmd):
        raise RuntimeError('extract command failed')

    if os.system(update_cmd):
        raise RuntimeError('update command failed')


if __name__ == '__main__':
    cli()


# Begin data commands
@cli.group()
def data():
    """Data related commands."""
    pass



@data.command(name='import')
@click.argument('source', type=click.Path(exists=True))
def import_data(source):
    """Import a backup file into the database.

    This does not check the input nor overwrite any existing data,
    but may cause conflicts.

    \b
    Args:
        source: backup file (JSON)
    """
    relations = {
        'pages': {},
        'posts': {}
    }

    with open(source, 'r', encoding='utf-8') as f:
        for line in [l.strip() for l in f if l.strip()]:
            struct = json.loads(line)
            entity = struct.get('entity')
            data = struct.get('data')

            if not data or not isinstance(data, dict):
                click.echo('[ERROR] Malformed data: {}'.format(line))
                continue

            if entity == 'user':
                new_user = User(
                    username=data['username'],
                    password=data['password'],
                    reset_password_token=data['reset_password_token'],
                    email=data['email'],
                    is_active=data['is_active'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    personal_bio=data['personal_bio'],
                    notify_login=data['notify_login'],
                )

                new_user.role_names = set(data['roles'])

                db.session.add(new_user)

            elif entity == 'page':
                new_page = Page(
                    title=data['title'],
                    mini=data['mini'],
                    route=data['route'],
                    custom_head=data['custom_head'],
                    content=data['content'],
                    is_published=data['is_published'],
                    comments_enabled=data['comments_enabled'],
                    last_updated=datetime.datetime.strptime(
                        data['last_updated'],
                        '%Y-%m-%d %H:%M:%S'
                    )
                )

                if data['ghosted']:
                    relations['pages'][data['route']] = data['ghosted']

                db.session.add(new_page)

            elif entity == 'post':
                new_post = Post(
                    title=data['title'],
                    slug=data['slug'],
                    content=data['content'],
                    is_published=data['is_published'],
                    comments_enabled=data['comments_enabled'],
                    last_updated=datetime.datetime.strptime(
                        data['last_updated'],
                        '%Y-%m-%d %H:%M:%S'
                    ),
                    tag_names=data['tags']
                )

                if data['ghosted']:
                    if data['slug'] not in relations['posts']:
                        relations['posts'][data['slug']] = {
                            'ghost': None,
                            'authors': None
                        }

                    relations['posts'][data['slug']]['ghost'] = data['ghosted']

                if data['authors']:
                    if data['slug'] not in relations['posts']:
                        relations['posts'][data['slug']] = {
                            'ghost': None,
                            'authors': None
                        }

                    relations['posts'][data['slug']]['authors'] = data['authors']

                db.session.add(new_post)

            elif entity == 'upload':
                new_upload = FileUpload(
                    path=data['path'],
                    description=data['description'],
                    mime=data['mime'],
                    uploaded_at=datetime.datetime.strptime(
                        data['uploaded_at'],
                        '%Y-%m-%d %H:%M:%S'
                    )
                )

                db.session.add(new_upload)

            else:
                click.echo('[ERROR] Invalid entity: {}'.format(line))
                continue

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

        click.echo('Error importing data')
        click.echo(e)

        return

    finally:
        if not correct:
            db.session.rollback()


    # Handle relations
    for route in relations['pages']:
        ghost_page = Page.query.filter_by(route=route).first()

        if not ghost_page:
            continue

        to_ghost = Page.query.filter_by(route=relations['pages'][route]).first()

        if not to_ghost:
            continue

        ghost_page.ghosted_id = to_ghost.id


    for slug in relations['posts']:
        post = Post.query.filter_by(slug=slug).first()

        if not post:
            continue

        if relations['posts'][slug]['ghost']:
            to_ghost = Post.query.filter_by(
                slug=relations['posts'][slug]['ghost']
            ).first()

            if to_ghost:
                post.ghosted_id = to_ghost.id

        if relations['posts'][slug]['authors']:
            authors = User.query.filter(
                User.username.in_(relations['posts'][slug]['authors'])
            )

            post.authors = [a for a in authors]

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

        click.echo('Error processing relations')
        click.echo(e)

        return

    finally:
        if not correct:
            db.session.rollback()

    click.echo('Finished data import!')
