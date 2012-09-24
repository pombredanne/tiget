import sys
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget import settings


def main():
    settings['color'] = sys.stdout.isatty()

    args = sys.argv[1:]
    if not args or args[0] == 'shell':
        Repl().run()
    else:
        Script(list2cmdline(args), '<argv>').run()
