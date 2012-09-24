import sys
import os
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget.settings import settings


def main():
    settings['color'] = sys.stdout.isatty()

    head, tail = os.getcwd(), '.'
    while tail:
        if os.path.exists(os.path.join(head, '.git')):
            settings['repository_path'] = head
            break
        head, tail = os.path.split(head)

    args = sys.argv[1:]
    if not args:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script(sys.stdin, '<stdin>')
    else:
        script = Script(list2cmdline(args), '<argv>')
    return script.run()
