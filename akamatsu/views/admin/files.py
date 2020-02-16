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

"""This module contains file views."""

import mimetypes
import os

from urllib.parse import unquote

from flask import abort, current_app, flash, jsonify, redirect, \
        render_template, request, url_for
from flask_babel import _
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from wtforms import ValidationError

from akamatsu import db
from akamatsu.models import FileUpload
from akamatsu.views.admin import bp_admin
from akamatsu.forms import UploadForm
from akamatsu.util import allowed_roles, is_allowed_file, is_ajax, is_safe_url


@bp_admin.route('/files')
@allowed_roles('administrator', 'blogger', 'editor')
def file_index():
    """Display a paginated list of files.

    If this endpoint is called from AJAX, only the requested page contents
    are returned.
    """
    page = request.args.get('page', 1, int)
    sort_key = request.args.get('sort')
    order_dir = request.args.get('order')

    # Users can see all files
    files = FileUpload.query

    files, sort_key, order_dir = _sort_files(files, sort_key, order_dir)
    files = files.paginate(page, current_app.config['PAGE_ITEMS'], False)

    if is_ajax():
        # AJAX request
        return render_template(
            'admin/files/partials/files_page.html',
            files=files,
            sort_key=sort_key,
            order_dir=order_dir
        )

    return render_template(
        'admin/files/index.html',
        files=files,
        sort_key=sort_key,
        order_dir=order_dir
    )


@bp_admin.route('/files/new', methods=['GET', 'POST'])
@allowed_roles('administrator', 'blogger', 'editor')
def upload_file():
    """Upload a new file."""
    form = UploadForm()

    if form.validate_on_submit():
        # Initial checks
        if not is_allowed_file(form.upload.data.filename):
            form.upload.errors.append(_('File type is not allowed'))
            return render_template('admin/files/edit.html', form=form)

        if form.filename.data:
            filename = secure_filename(form.filename.data)

            if not is_allowed_file(filename):
                form.filename.errors.append(_('File type is not allowed'))
                return render_template('admin/files/edit.html', form=form)

        else:
            filename = form.upload.data.filename

        rel_path = filename

        subdir = form.subdir.data

        if subdir:
            subdir = secure_filename(subdir)
            rel_path = os.path.join(subdir, rel_path)

        dst_path = os.path.join(current_app.config['UPLOADS_PATH'], rel_path)
        dst_dir = os.path.dirname(dst_path)

        if os.path.exists(dst_path):
            flash(_('A file in that path already exists'))
            return render_template('admin/files/edit.html', form=form)

        if not os.path.exists(dst_dir):
            # Create subdirectory
            try:
                os.mkdir(dst_dir)
                os.chmod(dst_dir, 0o755)

            except:
                flash(_('Failed to create subdirectory, contact an administrator'))
                return render_template('admin/files/edit.html', form=form)


        new_file = FileUpload(
            path=rel_path,
            description=form.description.data
        )

        if form.mime.data and form.mime.data in mimetypes.types_map.values():
            new_file.mime = form.mime.data

        else:
            _fname, ext = os.path.splitext(filename)
            new_file.mime = mimetypes.types_map.get(ext, 'UNKNOWN')

        try:
            correct = True
            db.session.add(new_file)
            db.session.commit()

            form.upload.data.save(dst_path)
            os.chmod(dst_path, 0o644)

            flash(_('New file uploaded correctly'), 'success')

            return redirect(url_for('admin.file_index'))

        except IntegrityError:
            # Path already exists
            # Need to manually rollback here
            db.session.rollback()
            form.route.errors.append(_('File in that path already exists'))

            return render_template('admin/files/edit.html', form=form)

        except Exception:
            # Catch anything unknown
            correct = False

            flash(_('Failed to upload file, contact an administrator'), 'error')

            return render_template('admin/files/edit.html', form=form)

        finally:
            if not correct:
                db.session.rollback()

    return render_template('admin/files/edit.html', form=form)


@bp_admin.route('/files/<hashid>')
@allowed_roles('administrator', 'blogger', 'editor')
def show_file(hashid):
    """Show an existing file.

    Files cannot be edited, so they must be deleted and reuploaded.

    Args:
        hashid (str): HashID of the file.
    """
    fupload = FileUpload.get_by_hashid(hashid)

    if not fupload:
        flash(_('Could not find file'), 'error')

        return redirect(url_for('admin.file_index'))

    return render_template('admin/files/show.html', fupload=fupload)


@bp_admin.route('/files/<hashid>/delete', methods=['GET', 'POST'])
@allowed_roles('administrator', 'blogger', 'editor')
def delete_file(hashid):
    """Delete a file.

    Usual flow is by calling this endpoint from AJAX (button in file listing).

    If the query parameter "ref" is set, the browser will be redirected to that
    URL after deletion (if it is safe).

    Args:
        hashid (str): HashID of the file.
    """
    fupload = FileUpload.get_by_hashid(hashid)

    if not fupload:
        flash(_('Could not find file'), 'error')

        return redirect(url_for('admin.file_index'))

    if request.method == 'POST':
        # Delete file
        ref = unquote(request.args.get('ref', ''))

        try:
            correct = True
            db.session.delete(fupload)
            db.session.commit()

            # Delete from file system
            fpath = os.path.join(
                current_app.config['UPLOADS_PATH'],
                fupload.path
            )

            if os.path.isfile(fpath):
                os.unlink(fpath)

            flash(_('File deleted'), 'success')

            # Redirect user
            if ref and is_safe_url(ref):
                # Provided as query parameter
                if is_ajax():
                    return jsonify({'redirect': ref}), 200

                return redirect(ref)

            # Default to index
            if is_ajax():
                return jsonify({'redirect': url_for('admin.file_index')}), 200

            return redirect(url_for('admin.file_index'))

        except ValidationError:
            # CSRF invalid
            correct = False
            current_app.logger.exception('Failed to delete file')

            flash(_('Failed to delete file, invalid CSRF token received'), 'error')

        except OSError:
            # Failed to delete file
            correct = False
            current_app.logger.exception('Failed to remove file from filesystem')

            flash(_('Failed to delete file, contact an administrator'), 'error')

        except Exception:
            # Catch anything unknown
            correct = False
            current_app.logger.exception('Failed to delete file')

            flash(_('Failed to delete file, unknown error encountered'), 'error')

        finally:
            if not correct:
                # Cleanup and show error
                db.session.rollback()

                # Check AJAX
                if is_ajax():
                    abort(400)

                return redirect(
                    url_for('admin.show_file', hashid=hashid)
                )

    # Check AJAX
    if is_ajax():
        return render_template(
            'admin/files/partials/delete_modal.html',
            fupload=fupload,
            ref=request.args.get('ref', '')
        )

    return render_template(
        'admin/files/delete.html',
        fupload=fupload
    )


def _sort_files(query, key, order):
    """Sort files according to the specified key and order.

    Args:
        query: Original query to order.
        key (str): Key to order by.
        order (str): Order direction ("asc" or "desc").

    Returns:
        Tuple with ordered query, key, and order.
    """
    ordering = None

    if key == 'path':
        # Order by path
        ordering = FileUpload.path

    elif key == 'mime':
        # Order by MIME type
        ordering = FileUpload.mime

    elif key == 'date':
        # Order by date
        ordering = FileUpload.uploaded_at

    else:
        # Order by date and don't set ordering
        return query.order_by(FileUpload.uploaded_at.desc()), None, None

    # Ordering
    if order == 'asc':
        return query.order_by(ordering), key, order

    order = 'desc'
    return query.order_by(ordering.desc()), key, order
