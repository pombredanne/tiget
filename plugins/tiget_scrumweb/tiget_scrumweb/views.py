from functools import wraps

from bottle import get, post, request, template

from tiget_scrumweb import aaa


def forceauth(fn):
    @wraps(fn)
    def _inner(*args, **kwargs):
        aaa.require(fail_redirect='/login')
        return fn(*args, **kwargs)
    return _inner


@get('/login')
@post('/login')
def login():
    username = request.POST.get('user')
    password = request.POST.get('password')
    if username is None:
        return template('login')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')


@get('/logout')
@forceauth
def logout():
    aaa.current_user.logout(redirect='/login')


@get('/')
@forceauth
def index():
    return template('index')
