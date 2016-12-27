from flask import request, redirect

from mserve import get_st


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


