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

"""This file contains the view for the ``settings`` section of the dashboard."""

from akamatsu import db
from akamatsu.forms import SettingsForm
from akamatsu.views.dashboard import bp_dashboard

from flask import current_app, render_template
from flask_user import roles_required
from sqlalchemy.exc import SQLAlchemyError


@bp_dashboard.route('/settings', methods=['GET', 'POST'])
@roles_required('admin')
def settings_edit():
    """Show the form for editing site settings."""
    # Get current values
    state = current_app.extensions['waffleconf']

    parsed = state.parse_conf()
    social = '\n'.join(
        ['%s:%s' % (a.get('glyph',''), a.get('link','')) for a in parsed.get('SOCIAL', [])])
    navbar = '\n'.join(
        ['%s:%s' % (a.get('text',''), a.get('link','')) for a in parsed.get('NAVBAR', [])])

    populate = {
        'sitename': parsed.get('SITENAME', ''),
        'social': social,
        'navbar': navbar,
        'allowed_extensions': ','.join(parsed.get('ALLOWED_EXTENSIONS', set())),
        'disqus_shortname': parsed.get('DISQUS_SHORTNAME', ''),
        'humans': parsed.get('HUMANS_TXT', ''),
        'robots': parsed.get('ROBOTS_TXT', ''),
        'footer_left': parsed.get('FOOTER_LEFT', ''),
        'footer_right': parsed.get('FOOTER_RIGHT', ''),
    }

    form = SettingsForm(**populate)

    if form.validate_on_submit():
        # Update configs
        new_social = []
        if form.social.data:
            for s in form.social.data.split('\n'):
                split = s.split(':', 1)
                try:
                    new_social.append({
                        'glyph': split[0].strip(),
                        'link': split[1].strip()
                    })

                except:
                    # Skip this element, it was not well written
                    pass

        new_navbar = []
        if form.navbar.data:
            for s in form.navbar.data.split('\n'):
                split = s.split(':', 1)
                try:
                    new_navbar.append({
                        'text': split[0].strip(),
                        'link': split[1].strip()
                    })

                except:
                    # Skip this element, it was not well written
                    pass

        new_extensions = []

        if form.allowed_extensions.data:
            new_extensions = [
                a.strip() for a in form.allowed_extensions.data.split(',')]

        to_store = {
            'SITENAME': form.sitename.data,
            'SOCIAL': new_social,
            'NAVBAR': new_navbar,
            'ALLOWED_EXTENSIONS': set(new_extensions),
            'DISQUS_SHORTNAME': form.disqus_shortname.data,
            'HUMANS_TXT': form.humans.data,
            'ROBOTS_TXT': form.robots.data,
            'FOOTER_LEFT': form.footer_left.data,
            'FOOTER_RIGHT': form.footer_right.data,
        }

        try:
            correct = True
            state.update_db(to_store)

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
                    'akamatsu/dashboard/settings/edit.html',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg)


        # Settings saved, remain in the edition view
        return render_template(
            'akamatsu/dashboard/settings/edit.html',
            status='saved',
            form=form)

    return render_template(
        'akamatsu/dashboard/settings/edit.html',
        status='edit',
        form=form)
