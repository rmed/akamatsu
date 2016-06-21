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

"""This file contains the view for the ``profile`` section of the dashboard."""

from akamatsu import db
from akamatsu.forms import ProfileForm
from akamatsu.models import User
from akamatsu.views.dashboard import bp_dashboard

from flask import render_template
from flask_user import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError


@bp_dashboard.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """Show the form for editing profile of the current user."""
    user = User.query.filter_by(id=current_user.id).first()

    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        # Check model can be saved
        form.populate_obj(user)

        try:
            correct = True
            db.session.commit()

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
                    'akamatsu/dashboard/profile/edit.html',
                    status='saveerror',
                    form=form,
                    errmsg=errmsg,
                    user_id=user.id)


        # Profile saved, remain in the edition view
        return render_template(
            'akamatsu/dashboard/profile/edit.html',
            status='saved',
            form=form,
            user_id=user.id)

    return render_template(
        'akamatsu/dashboard/profile/edit.html',
        status='edit',
        form=form,
        user_id=user.id)
