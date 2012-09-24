import sys
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget.settings import settings
from tiget.utils import find_repository_path


def main():
    settings['color'] = sys.stdout.isatty()

    repository_path = find_repository_path()
    if repository_path:
        settings['repository_path'] = repository_path

    args = sys.argv[1:]
    if not args:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script(sys.stdin, '<stdin>')
    else:
        script = Script(list2cmdline(args), '<argv>')
    return script.run()
