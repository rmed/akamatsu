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

from flask import current_app, render_template
from flask_user import roles_required
from sqlalchemy.exc import SQLAlchemyError

from akamatsu import db
from akamatsu.forms import SettingsForm
from akamatsu.views.dashboard import bp_dashboard


@bp_dashboard.route('/settings')
@roles_required('admin')
def settings_show():
    """Show current application settings"""
    config = current_app.config

    social = '\n'.join(
        ['%s:%s' % (a.get('glyph',''), a.get('link','')) for a in config.get('SOCIAL', [])]
    )
    navbar = '\n'.join(
        ['%s:%s' % (a.get('text',''), a.get('link','')) for a in config.get('NAVBAR', [])]
    )

    isso_reply_self = True if config.get('ISSO_REPLY_SELF', 'false') == 'true' else False
    isso_require_author = True if config.get('ISSO_REQUIRE_AUTHOR', 'false') == 'true' else False
    isso_require_email = True if config.get('ISSO_REQUIRE_EMAIL', 'false') == 'true' else False
    isso_voting = True if config.get('ISSO_VOTING', 'false') == 'true' else False

    populate = {
        'sitename': config.get('SITENAME', ''),
        'social': social,
        'navbar': navbar,
        'allowed_extensions': ','.join(config.get('ALLOWED_EXTENSIONS', set())),
        'comment_system': config.get('COMMENT_SYSTEM', ''),
        'disqus_shortname': config.get('DISQUS_SHORTNAME', ''),
        'isso_url': config.get('ISSO_URL', ''),
        'isso_reply_self': isso_reply_self,
        'isso_require_author': isso_require_author,
        'isso_require_email': isso_require_email,
        'isso_voting': isso_voting,
        'humans': config.get('HUMANS_TXT', ''),
        'robots': config.get('ROBOTS_TXT', ''),
        'footer_left': config.get('FOOTER_LEFT', ''),
        'footer_right': config.get('FOOTER_RIGHT', ''),
    }

    form = SettingsForm(**populate)

    return render_template(
        'akamatsu/dashboard/settings/show.html',
        form=form
    )
