import sys
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget import settings


def main():
    settings['color'] = sys.stdout.isatty()

    args = sys.argv[1:]
    if not args:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script(sys.stdin, '<stdin>')
    else:
        script = Script(list2cmdline(args), '<argv>')
    return script.run()
