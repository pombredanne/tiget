import os
import sys
from subprocess import list2cmdline

from tiget.plugins import load_plugin
from tiget.script import Script, Repl
from tiget.conf import settings
from tiget.utils import print_error


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
    load_plugin('tiget.core')
    load_config()

    args = sys.argv[1:]
    if args:
        script = Script(list2cmdline(args), '<argv>')
    else:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script.from_file(sys.stdin)
    return script.run()
