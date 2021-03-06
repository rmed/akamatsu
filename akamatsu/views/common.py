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

"""This file contains common views."""

import os

from flask import Blueprint, current_app, make_response, send_from_directory
from werkzeug.utils import secure_filename

from akamatsu.models import FileUpload


bp_common = Blueprint('common', __name__)


@bp_common.route('/_uploads/<path:filename>')
def serve_file(filename):
    """Serve the given uploaded file.

    Args:
        filename (str): Relative file path.
    """
    fupload = FileUpload.get_by_path(filename)

    if not fupload:
        return make_response('', 404)

    return send_from_directory(
        current_app.config['UPLOADS_PATH'],
        filename,
        mimetype=fupload.mime
    )


@bp_common.route('/favicon.ico')
def favicon():
    """Serve favicon.

    This endpoint will return a 404 unless the `FAVICON_DIR` attribute
    is configured in the application and a "favicon.ico" file exists in
    that directory.

    Args:
        filename (str): Filename to serve.
    """
    fav_path = current_app.config.get('FAVICON_DIR')

    if not fav_path or not os.path.isdir(fav_path):
        return make_response('', 404)

    return send_from_directory(fav_path, 'favicon.ico')


@bp_common.route('/_favicon/<path:filename>')
def favicon_extras(filename):
    """Serve favicon related files.

    This endpoint will return a 404 unless the `FAVICON_DIR` attribute
    is configured in the application.

    Args:
        filename (str): Filename to serve.
    """
    fav_path = current_app.config.get('FAVICON_DIR')

    if not fav_path or not os.path.isdir(fav_path):
        return make_response('', 404)

    return send_from_directory(fav_path, secure_filename(filename))
