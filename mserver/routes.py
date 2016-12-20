from flask import Flask, request, redirect, render_template, make_response, send_file, after_this_request

import tempfile
import zipfile
from os import urandom
import os.path
from binascii import hexlify
from hashlib import sha256

from mserver import app, get_st


@app.route('/', methods=['GET', 'POST'])
def prompt_auth():
    st = get_st()
    if request.method == 'GET':
        if 'auth' in request.cookies and st.check_auth(request.cookies['auth']):
            return redirect("/search")
        else:
            return render_template('prompt_auth.jinja2')
    elif request.method == 'POST':
        password = request.form['password']
        key = st.redeem_auth(password)
        if key is None:
            return render_template('prompt_auth.jinja2', msg='nope, try again.')
        else:
            response = make_response(redirect('/search'))
            response.set_cookie('auth', key)
            return response


@app.route('/search', methods=['GET', 'POST'])
def search():
    st = get_st()
    if 'auth' not in request.cookies or not st.check_auth(request.cookies['auth']):
        return redirect("/")
    if request.method == 'GET':
        return render_template('search.jinja2')
    if request.method == 'POST':
        regex = request.form['regex']
        albums = st.search_albums(regex)
        return render_template('search_results.jinja2', albums=albums)


@app.route('/download/<int:album_id>', methods=['GET'])
def download(album_id):
    st = get_st()
    if 'auth' not in request.cookies or not st.check_auth(request.cookies['auth']):
        return redirect("/")
    name = st.get_album_desc(album_id)
    tmp = name + ' ' + hexlify(urandom(4)).decode('ascii') + '.zip'
    fname = os.path.join(app.config['ZIP_DIR'], tmp)
    zip = zipfile.ZipFile(fname, 'w')
    for path in st.get_files(album_id):
        # last = hexlify(urandom(2)).decode('ascii')
        # zip.write(path, arcname=os.path.join(tmp, os.path.basename(last + ' ' + path)))
        zip.write(path)
    zip.close()

    @after_this_request
    def cleanup(response):
        os.remove(fname)
        return response

    return send_file(fname, attachment_filename=tmp, as_attachment=True)


def check_admin_auth():
    if 'admin_nonce' not in request.cookies or 'admin_auth' not in request.cookies:
        return False
    nonce = request.cookies['admin_nonce'].encode('ascii')
    m = sha256()
    m.update(nonce)
    m.update(app.config['SUPER_SECRET'].encode('ascii'))
    cookie = hexlify(m.digest())
    return cookie == request.cookies['admin_auth'].encode('ascii')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if check_admin_auth():
        return render_template('admin_console.jinja2')
    if request.method == 'GET':
        return render_template('auth_admin.jinja2')
    if request.form['password'] != app.config['ADMIN_PASSWORD']:
        return render_template('auth_admin.jinja2', msg='nope. try again.')
    nonce = hexlify(urandom(16))
    m = sha256()
    m.update(nonce)
    m.update(app.config['SUPER_SECRET'].encode('ascii'))
    cookie = hexlify(m.digest())
    response = make_response(render_template('admin_console.jinja2'))
    response.set_cookie('admin_nonce', nonce)
    response.set_cookie('admin_auth', cookie)
    return response


@app.route('/ls_auth', methods=['GET'])
def ls_auth():
    if not check_admin_auth():
        return redirect('/auth_admin')
    auths = get_st().ls_auth()
    return render_template('ls_auth.jinja2', auths=auths)


@app.route('/mk_auth', methods=['GET', 'POST'])
def mk_auth():
    if not check_admin_auth():
        return redirect('/auth_admin')
    if request.method == 'GET':
        return render_template('mk_auth.jinja2')
    password = request.form['password']
    get_st().mk_auth(password)
    return redirect('/ls_auth')


@app.route('/rm_auth/<id>', methods=['GET'])
def rm_auth(id):
    if not check_admin_auth():
        return redirect('/auth_admin')
    get_st().rm_auth(id)
    return redirect('/ls_auth')
