from flask import request, redirect, render_template, send_file, after_this_request, jsonify, make_response

import os
import os.path
from binascii import hexlify
from functools import wraps
from uuid import UUID

from mserve import app, get_st
from mserve.zip import do_zip


def check_auth():
    return 'auth' in request.cookies and get_st().auth.check_auth(request.cookies['auth'])


def with_auth(f):
    @wraps(f)
    def g(*args, **kwargs):
        if check_auth():
        # if True:
            return f(*args, **kwargs)
        else:
            return redirect('/auth')
    return g


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    st = get_st()
    if request.method == 'GET':
        if check_auth():
            return redirect('/')
        else:
            return render_template('auth.jinja2')
    elif request.method == 'POST':
        password = request.form['password']
        key = st.auth.redeem_auth(password)
        if key is None:
            return render_template('auth.jinja2', invalid=True)
        else:
            response = make_response(redirect('/'))
            response.set_cookie('auth', key)
            return response


@app.route('/')
@with_auth
def home():
    return render_template('search.jinja2')


@app.route('/search')
@with_auth
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


@app.route('/download/<release>')
@with_auth
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
