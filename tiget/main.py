import os
import sys
from argparse import ArgumentParser, REMAINDER

from tiget import __version__
from tiget.git import is_repo_initialized
from tiget.repl import Repl
from tiget.conf import settings
from tiget.utils import print_error, load_file, post_mortem
from tiget.cmds import CmdError, cmd_execfile, cmd_execv
from tiget.plugins import load_plugin


def load_config():
    files = ['/etc/tigetrc', '~/.tigetrc', 'tiget:/config/tigetrc']
    repo = settings.core.repository
    if repo and repo.workdir:
        files.append(os.path.join(repo.workdir, '.tigetrc'))
    for filename in files:
        try:
            f = load_file(filename)
        except IOError:
            continue
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
        '-v', '--version', action='store_true', dest='print_version',
        default=False, help='print version information')
    parser.add_argument('cmd', nargs=REMAINDER, help='execute a command')

    args = parser.parse_args()

    if args.print_version:
        print('tiget {}'.format(__version__))
        return

    load_plugin('tiget.core')

    if not is_repo_initialized():
        print_error('repository is not initialized; use tiget-setup')
        sys.exit(1)

    try:
        if args.load_config:
            load_config()

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
        post_mortem()
        sys.exit(1)
