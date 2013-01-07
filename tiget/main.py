import os
import sys
from argparse import ArgumentParser, REMAINDER
from subprocess import list2cmdline

from tiget.plugins import load_plugin
from tiget.script import Script, Repl


def load_config():
    files = [
        '/etc/tigetrc',
        os.path.expanduser('~/.tigetrc'),
    ]
    for filename in files:
        try:
            script = Script.from_file(filename)
        except IOError:
            pass
        else:
            script.run()


def main():
    parser = ArgumentParser(description='ticketing system with git backend')
    parser.add_argument(
        '-n', '--no-config', action='store_false', dest='load_config',
        default=True, help='prevent loading of default configuration files')
    parser.add_argument('cmd', nargs=REMAINDER, help='execute a command')

    args = parser.parse_args()

    load_plugin('tiget.core')
    if args.load_config:
        load_config()

    if args.cmd:
        script = Script(list2cmdline(args.cmd), '<argv>')
    else:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script.from_file(sys.stdin)
    return script.run()
