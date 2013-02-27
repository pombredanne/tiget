import os
import sys
from argparse import ArgumentParser, REMAINDER

from tiget.version import VERSION
from tiget.repl import Repl
from tiget.conf import settings
from tiget.utils import print_error, load_file, post_mortem
from tiget.cmds import cmd_execfile, cmd_execv


def load_config():
    files = [
        '/etc/tigetrc',
        os.path.expanduser('~/.tigetrc'),
    ]
    for filename in files:
        try:
            f = load_file(filename)
        except IOError:
            pass
        else:
            cmd_execfile(f)


def main():
    parser = ArgumentParser(description='ticketing system with git backend')
    parser.add_argument(
        '-i', '--interactive', action='store_true', default=sys.stdin.isatty(),
        help='force start of an interactive session, even if stdin is no tty')
    parser.add_argument(
        '-n', '--no-config', action='store_false', dest='load_config',
        default=True, help='prevent loading of default configuration files')
    parser.add_argument(
        '-o', '--add-option', action='append', dest='options',
        default=[], help='set an option for this session')
    parser.add_argument(
        '-v', '--version', action='store_true', dest='print_version',
        default=False, help='print version information')
    parser.add_argument('cmd', nargs=REMAINDER, help='execute a command')

    args = parser.parse_args()

    if args.print_version:
        print('tiget {}'.format(VERSION))
        return

    try:
        if args.load_config:
            load_config()

        for var in args.options:
            try:
                settings.parse_and_set(var)
            except (ValueError, KeyError) as e:
                print_error(e)

        if args.cmd:
            cmd_execv(args.cmd)
        elif args.interactive:
            Repl().run()
        else:
            cmd_execfile(sys.stdin)
    except CmdError as e:
        print_error(e)
        sys.exit(1)
    except Exception as e:
        print_error('internal error (see traceback)')
        post_mortem()
        sys.exit(1)
