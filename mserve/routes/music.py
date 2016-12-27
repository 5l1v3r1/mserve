from flask import request, render_template, send_file, after_this_request, jsonify

import os
import os.path
from binascii import hexlify
from uuid import UUID

from mserve import app, get_st
from mserve.zip import do_zip
from mserve.routes.common import with_auth


@with_auth
@app.route('/')
def home():
    return render_template('search.jinja2')


@with_auth
@app.route('/search')
def search():

    title_re = request.args.get('title') or None
    artist_re = request.args.get('artist') or None
    genre_re = request.args.get('genre') or None

    f = request.args.get('year_from')
    t = request.args.get('year_to')
    year_from = int(f) if f else None
    year_to = int(t) if t else None

    results = get_st().music.query(
            title_re=title_re,
            artist_re=artist_re,
            genre_re=genre_re,
            year_from=year_from,
            year_to=year_to,
            )

    return jsonify(results=results)


@with_auth
@app.route('/download/<release>')
def download(release):

    r = UUID(release)
    m = get_st().music
    desc = m.describe(r)
    out_path = os.path.join(app.config['ZIP_DIR'], hexlify(os.urandom(16)).decode('ascii'))
    in_paths = m.files_of(r)
    z = do_zip(in_paths, out_path, desc)

    @after_this_request
    def cleanup(response):
        os.remove(out_path)
        return response

    return send_file(out_path, attachment_filename=(desc + '.zip'), as_attachment=True)
