import os
import sys
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget.conf import settings
from tiget.utils import print_error
from tiget.git import GitError, auto_transaction, get_transaction


def load_config():
    files = [
        '/etc/tigetrc',
        'tiget:/config/tigetrc',
        os.path.expanduser('~/.tigetrc'),
    ]
    workdir = settings.core.workdir
    if workdir:
        files.append(os.path.join(workdir, '.tigetrc'))
    for filename in files:
        try:
            Script.from_file(filename).run()
        except IOError:
            pass


def main():
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
