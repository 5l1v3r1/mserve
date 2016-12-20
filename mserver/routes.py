from flask import Flask, request, redirect, render_template, make_response

from os import urandom
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


@app.route('/download/<album_id>', methods=['GET'])
def download(album_id):
    st = get_st()
    if 'auth' not in request.cookies or not st.check_auth(request.cookies['auth']):
        return redirect("/")
    pass


def check_admin_auth():
    nonce = request.cookies['admin_nonce'].encode('ascii')
    m = sha256()
    m.update(nonce)
    m.update(app.config['SUPER_SECRET'].encode('ascii'))
    cookie = hexlify(m.digest())
    return cookie == request.cookies['admin_auth'].encode('ascii')


@app.route('/admin', methods=['GET', 'POST'])
def auth_admin():
    if check_admin_auth():
        return redirect('/ls_auth')
    if request.method == 'GET':
        return render_template('auth_admin.jinja2')
    if request.form['password'] != app.config['ADMIN_PASSWORD']:
        return render_template('auth_admin.jinja2', msg='nope. try again.')
    nonce = hexlify(urandom(16))
    m = sha256()
    m.update(nonce)
    m.update(app.config['SUPER_SECRET'].encode('ascii'))
    cookie = hexlify(m.digest())
    response = make_response(redirect('/ls_auth'))
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
