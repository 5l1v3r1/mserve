from flask import Flask, request, redirect, render_template, make_response, send_file, after_this_request

from os import urandom
import os.path
from binascii import hexlify
from uuid import UUID

from mserve import app, get_st
from mserve.zip import do_zip


def check_auth():
    return 'auth' in request.cookies and get_st().auth.check_auth(request.cookies['auth'])


def with_auth(f):
    def g(*args, **kwargs):
        # if check_auth():
        if True:
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
            return render_template('auth.jinja2', msg='nope, try again.')
        else:
            response = make_response(redirect('/'))
            response.set_cookie('auth', key)
            return response


@app.route('/')
@with_auth
def root():
    return 'foo'


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
