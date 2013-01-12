from getpass import getpass

import bottle
from beaker.middleware import SessionMiddleware
from cryptacular.bcrypt import BCRYPTPasswordManager

from tiget.cmds import Cmd
from tiget.conf import settings
from tiget.scrum.models import User

from tiget_scrumweb import initialize


class RunServer(Cmd):
    description = 'start web server'

    def setup(self):
        self.parser.add_argument('-b', '--bind', default='localhost')
        self.parser.add_argument('-p', '--port', default=8000, type=int)
        self.parser.add_argument('-q', '--quiet', action='store_true')

    def do(self, args):
        initialize()
        if settings.core.debug:
            bottle.debug(True)
        session_opts = {
            'session.type': 'cookie',
            'session.validate_key': True,
            'session.cookie_expires': True,
            'session.timeout': 3600,    # 1 hour
        }
        app = SessionMiddleware(bottle.default_app(), session_opts)
        bottle.run(app=app, host=args.bind, port=args.port, quiet=args.quiet)


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

        manager = BCRYPTPasswordManager()
        hashed = manager.encode(password)

        conf_file = os.path.expanduser(settins.scrumweb.password_file)
        with open(conf_file, 'a') as f:
            f.write('{} {}'.format(user.email, password))
