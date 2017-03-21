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

"""This file contains the views for managing file uploads."""

from akamatsu import db
from akamatsu.forms import UploadForm
from akamatsu.models import FileUpload
from akamatsu.util import is_allowed_file
from akamatsu.views.dashboard import bp_dashboard

from flask import current_app, render_template, request
from flask_user import roles_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug import secure_filename
from werkzeug.exceptions import NotFound

import os


@bp_dashboard.route('/files')
@bp_dashboard.route('/files/<int:page>')
@roles_required(['admin', 'uploader', 'superuploader'])
def file_index(page=1):
    """Show available actions regarding files.

    Args:
        page (int): Listing page number to show.
    """
    order_key, order_dir, ordering = _sort_uploads(request.args)

    files = (
        FileUpload.query
        .order_by(ordering)
        .paginate(page, 20, False))

    try:
        return render_template(
            'akamatsu/dashboard/file/index.html',
            files=files,
            order_key=order_key,
            order_dir=order_dir)

    except NotFound:
        # Show a 'no files found' notice instead of a 404 error
        return render_template('akamatsu/dashboard/file/index.html')

@bp_dashboard.route('/files/delete/<int:file_id>', methods=['GET', 'POST'])
@roles_required(['admin', 'uploader', 'superuploader'])
def file_delete(file_id):
    """Confirm deletion of a file.

    GET requests show a message to confirm and POST requests delete the file
    and redirect back to index.

    Args:
        file_id (int): ID of the file to delete.
    """
    upload = FileUpload.query.filter_by(id=file_id).first()

    if not upload:
        # Show error message
        return render_template(
            'akamatsu/dashboard/file/delete.html',
            status='error',
            errmsg = 'File with ID %d does not exist' % file_id)

    path = os.path.join(current_app.config['UPLOAD_DIR'], upload.path)

    if request.method == 'POST':
        # Delete file
        try:
            correct = True
            db.session.delete(upload)
            db.session.commit()

            if os.path.exists(path):
                os.remove(path)

        except SQLAlchemyError as e:
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
                    'akamatsu/dashboard/file/delete.html',
                    status='error',
                    errmsg=errmsg)


        return render_template(
            'akamatsu/dashboard/file/delete.html', status='deleted')

    # Show confirmation
    return render_template(
        'akamatsu/dashboard/file/delete.html', status='confirm', file=upload)

@bp_dashboard.route('/files/view/<int:file_id>')
@roles_required(['admin', 'uploader', 'superuploader'])
def file_show(file_id):
    """Show details of a file.

    Args:
        file_id (int): ID of the file to show.
    """
    upload = FileUpload.query.filter_by(id=file_id).first()

    if not upload:
        # Return error message
        return render_template(
            'akamatsu/dashboard/file/show.html',
            status='error',
            errmsg='File does not exist')


    return render_template(
        'akamatsu/dashboard/file/show.html',
        status='ok',
        file=upload)

@bp_dashboard.route('/files/upload', methods=['GET', 'POST'])
@roles_required(['admin', 'uploader', 'superuploader'])
def file_upload():
    """Upload a file to the server."""
    form = UploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.filename.data)
        subdir = secure_filename(form.subdir.data)

        ul_filename = secure_filename(form.upload.data.filename)

        if not filename:
            # Use uploaded file name when storing
            filename = ul_filename

        if not is_allowed_file(filename) or not is_allowed_file(ul_filename):
            # Extension not allowed
            return render_template(
                'akamatsu/dashboard/file/upload.html',
                status='saveerror',
                form=form,
                errmsg='That file extension is not allowed')


        # Check paths
        dst_path = current_app.config['UPLOAD_DIR']
        if subdir:
            dst_path = os.path.join(dst_path, subdir)

            if not os.path.exists(dst_path):
                # Create subdir
                try:
                    os.mkdir(dst_path)
                    os.chmod(dst_path, 755)

                except:
                    return render_template(
                        'akamatsu/dashboard/file/upload.html',
                        status='saveerror',
                        form=form,
                        errmsg='Could not create subdirectory')

        dst_path = os.path.join(dst_path, filename)

        if os.path.exists(dst_path):
            # We do not overwrite anything
            return render_template(
                'akamatsu/dashboard/file/upload.html',
                status='saveerror',
                form=form,
                errmsg='A file with that name already exists')

        new_file = FileUpload(
            path=os.path.join(subdir, filename),
            description=form.description.data)

        # Store file
        try:
            db.session.add(new_file)
            db.session.commit()

            form.upload.data.save(dst_path)
            os.chmod(dst_path, 644)

        except:
            db.session.rollback()

            return render_template(
                'akamatsu/dashboard/file/upload.html',
                status='saveerror',
                form=form,
                errmsg='Failed to save file')

        # Saved correctly
        return render_template(
            'akamatsu/dashboard/file/upload.html',
            status='saved',
            form=form)


    return render_template('akamatsu/dashboard/file/upload.html', form=form)

def _sort_uploads(args):
    """Sort uploads according to the specified key and order.

    Args:
        args(dict): Arguments from the ``request`` object.

    Returns:
        Tuple with key, order and ordering to apply in query ``order_by()``.
    """
    key = args.get('orderby')
    order = args.get('order')
    result = None

    if key == 'date':
        # Order by date
        result = FileUpload.timestamp

    else:
        # Order by path
        key = 'path'
        result = FileUpload.path


    # Ordering
    if order == 'asc':
        return key, order, result

    order = 'desc'
    return key, order, result.desc()
