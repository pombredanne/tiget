from functools import wraps
import os

from bottle import get, post, request, redirect, template
from tiget.conf import settings

from tiget_scrumweb.password import check_password


def forceauth(fn):
    @wraps(fn)
    def _inner(*args, **kwargs):
        session = request.environ.get('beaker.session')
        if session.get('user') is None:
            redirect('/login')
        settings.scrum.current_user = user
        return fn(*args, **kwargs)
        settins.scrum.current_user = None
    return _inner


@get('/login')
@post('/login')
def login():
    if request.method == 'POST':
        username = request.POST.get('user', '')
        password = request.POST.get('password', '')
        if check_password(username, password):
            session = request.environ.get('beaker.session')
            session['user'] = username
            session.save()
            redirect('/')
        redirect('/login')
    return template('login')


@get('/logout')
@forceauth
def logout():
    session = request.environ.get('beaker.session')
    session.delete()
    redirect('/login')


@get('/')
@forceauth
def index():
    return template('index')
