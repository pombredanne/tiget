import os
import sys
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget.settings import settings
from tiget.utils import print_error
from tiget.git import GitError, find_repository_path
from tiget.plugins import load_plugin


def load_config():
    files = [
        '/etc/tigetrc',
        'tiget:/config/tigetrc',
        os.path.expanduser('~/.tigetrc'),
        os.path.join(settings.core.repository_path, '.tigetrc'),
    ]
    for filename in files:
        try:
            Script.from_file(filename).run()
        except IOError:
            pass


def main():
    try:
        settings.core.repository_path = find_repository_path()
        load_config()
    except GitError as e:
        print_error(e)
        return 1

    args = sys.argv[1:]
    if args:
        script = Script(list2cmdline(args), '<argv>')
    else:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script.from_file(sys.stdin)
    return script.run()
