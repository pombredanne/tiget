from getpass import getpass

from bottle import debug, default_app, run
from beaker.middleware import SessionMiddleware
from tiget.cmds import Cmd
from tiget.conf import settings
from tiget.scrum.models import User

from tiget_scrumweb.password import set_password


class RunServer(Cmd):
    description = 'start web server'

    def setup(self):
        self.parser.add_argument('-b', '--bind', default='localhost')
        self.parser.add_argument('-p', '--port', default=8000, type=int)
        self.parser.add_argument('-q', '--quiet', action='store_true')

    def do(self, args):
        settings.scrum.current_user = None
        if settings.core.debug:
            debug(True)
        session_opts = {
            'session.type': 'cookie',
            'session.validate_key': True,
            'session.cookie_expires': True,
            'session.timeout': 3600,    # 1 hour
        }
        app = SessionMiddleware(default_app(), session_opts)
        run(app=app, host=args.bind, port=args.port, quiet=args.quiet)


class SetPassword(Cmd):
    description = 'set the password for a user'

    def setup(self):
        self.parser.add_argument('email')

    def do(self, args):
        try:
            user = User.objects.get(email=args.email)
        except User.DoesNotExist:
            raise self.error(e)
        try:
            password = getpass('Password: ')
            password_again = getpass('Password (again): ')
        except (KeyboardInterrupt, EOFError):
            raise self.error('interrupted')
        if not password == password_again:
            raise self.error('passwords do not match')
        set_password(user.email, password)
