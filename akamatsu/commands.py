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

"""This file contains custom command definitions for akamatsu."""

from flask.cli import FlaskGroup

from akamatsu import db, user_manager, init_app
from akamatsu.models import User
from akamatsu.util import ROLE_NAMES

import click
import datetime


def init_wrapper(info):
    """Wrapper for the application initialization function."""
    return init_app()


@click.group(cls=FlaskGroup, create_app=init_wrapper)
def cli():
    """Management script."""
    pass


@cli.command()
@click.option('--username', help='username (must be unique)', prompt=True)
@click.option('--email', help='email (must be unique)', prompt=True)
@click.option('--password', help='password', prompt=True, hide_input=True)
def adduser(username, email, password):
    """Add a new user to the database."""
    hashed_password = user_manager.hash_password(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        confirmed_at=datetime.datetime.now(),
        is_enabled=True,
        notify_login=False
    )

    try:
        correct = True
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        # Catch anything unknown
        correct = False
        click.echo(e)

    finally:
        if not correct:
            # Cleanup and show error
            db.session.rollback()

            click.echo(
                'Error creating user, make sure username and email are unique'
            )

        else:
            click.echo('New user created')

@cli.command()
@click.argument('username')
def rmuser(username):
    """Remove a user from the database."""
    user = User.query.filter_by(username=username).first()

    if not user:
        click.echo('User does not exist')
        return

    if not click.confirm('Do you want to continue?'):
        return

    try:
        correct = True
        db.session.delete(user)
        db.session.commit()

    except Exception as e:
        # Catch anything unknown
        correct = False
        click.echo(e)

    finally:
        if not correct:
            # Cleanup and show error
            db.session.rollback()

            click.echo(
                'Error removing user'
            )

        else:
            click.echo('User removed')

@cli.command()
def listroles():
    """List roles available in the application."""
    click.echo('Roles:\n')

    for role in ROLE_NAMES:
        click.echo('- %s' % role)

@cli.command()
@click.argument('username')
@click.argument('roles')
def setroles(username, roles):
    """Set roles for a given user.

    This overrides current roles of the user.

    NOTE: only roles recognized by the application are accepted.

    \b
    Args:
        username: the username to set roles for
        roles: comma separated role names (e.g. blogger,editor)
    """
    user = User.query.filter_by(username=username).first()

    if not user:
        click.echo('User does not exist')
        return

    # Update roles
    new_roles = set([n.strip() for n in roles.split(',')]) & set(ROLE_NAMES)

    user.role_names = new_roles

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        # Catch anything unknown
        correct = False
        click.echo(e)

    finally:
        if not correct:
            # Cleanup and show error
            db.session.rollback()

            click.echo('Error updating roles')

        else:
            click.echo('Roles updated')

@cli.command()
@click.argument('username')
def showroles(username):
    """Show roles of a given user.

    \b
    Args:
        username: the username to list roles for
    """
    user = User.query.filter_by(username=username).first()

    if not user:
        click.echo('User does not exist')
        return

    roles = ', '.join(user.role_names) or 'No roles'

    click.echo('Roles of user "%s": %s' % (username, roles))


if __name__ == '__main__':
    cli()
