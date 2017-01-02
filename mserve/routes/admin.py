from flask import request, redirect, render_template, make_response

import os
import os.path
from binascii import hexlify
from functools import wraps
from hashlib import sha256

from mserve.app import app, get_st


def check_admin_auth():
    if 'admin_nonce' not in request.cookies or 'admin_auth' not in request.cookies:
        return False
    nonce = request.cookies['admin_nonce'].encode('ascii')
    m = sha256()
    m.update(nonce)
    m.update(app.config['SUPER_SECRET'].encode('ascii'))
    cookie = hexlify(m.digest())
    return cookie == request.cookies['admin_auth'].encode('ascii')


def with_admin_auth(f):
    @wraps(f)
    def g(*args, **kwargs):
        if check_admin_auth():
            return f(*args, **kwargs)
        else:
            return redirect('/admin/auth')
    return g


@app.route('/admin/auth', methods=['GET', 'POST'])
def admon_auth():
    if request.method == 'GET':
        return (
            redirect('/admin')
            if check_admin_auth()
            else render_template('admin/auth.jinja2')
            )
    if request.form.get('password') != app.config['ADMIN_PASSWORD']:
        return render_template('admin/auth.jinja2', invalid=True)
    nonce = hexlify(os.urandom(16))
    m = sha256()
    m.update(nonce)
    m.update(app.config['SUPER_SECRET'].encode('ascii'))
    cookie = hexlify(m.digest())
    response = make_response(redirect('/admin'))
    response.set_cookie('admin_nonce', nonce)
    response.set_cookie('admin_auth', cookie)
    return response


@app.route('/admin/unauth')
@with_admin_auth
def admin_unauth():
    response = make_response(redirect('/admin'))
    response.set_cookie('admin_nonce', expires=0)
    response.set_cookie('admin_auth', expires=0)
    return response


@app.route('/admin')
@with_admin_auth
def admin_console():
    show = 'show' in request.args
    auths = get_st().auth.ls_auth() if 'show' in request.args else None
    return render_template('admin/console.jinja2', auths=auths)


@app.route('/admin/mk_auth', methods=['POST'])
@with_admin_auth
def mk_auth():
    password = request.form['password']
    get_st().auth.mk_auth(password)
    return redirect('/admin')


@app.route('/admin/rm_auth/<id>')
@with_admin_auth
def rm_auth(id):
    get_st().auth.rm_auth(id)
    return redirect('/admin')
