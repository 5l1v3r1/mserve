from flask import Flask, request, redirect, render_template, make_response

from mserver import app, get_st


@app.route('/', methods=['GET', 'POST'])
def prompt_auth():
    st = get_st()
    if request.method == 'GET':
        if 'auth' in request.cookies and st.check_auth(request.cookies['auth']):
            return redirect("/search")
        else:
            return render_template('prompt_auth.jinja2')
    if request.method == 'POST':
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
