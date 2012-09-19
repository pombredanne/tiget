import os
import sys
import readline
import shlex
import traceback

from colors import red, green

from tiget import get_version, settings, aliases
from tiget.cmds import commands, CmdError, run


class Interpreter(object):
    def print_error(self, line):
        if settings.color and sys.stderr.isatty():
            line = red(line)
        print >> sys.stderr, line

    def run(self, line):
        if line[0] in aliases:
            line = shlex.split(aliases[line[0]]) + line[1:]
        try:
            run(line)
        except CmdError as e:
            self.print_error(str(e))
        except Exception:
            traceback.print_exc()

    def exec_line(self, line):
        try:
            line = shlex.split(line)
        except ValueError as e:
            self.print_error('Syntax error: {}'.format(e))
        else:
            if line:
                self.run(line)


class Repl(Interpreter):
    def complete(self, text, state):
        cmds = commands.keys() + aliases.keys()
        options = [cmd for cmd in cmds if cmd.startswith(text)]
        if state < len(options):
            return options[state] + ' '
        return None

    def run_loop(self):
        print 'tiget {}'.format(get_version())
        print 'Type "help" for help.'
        print ''
        readline.parse_and_bind('tab: complete')
        while True:
            prompt = 'tiget% '
            if settings.color and sys.stdout.isatty():
                prompt = green(prompt)
            readline.set_completer(self.complete)
            try:
                line = raw_input(prompt).strip()
            except KeyboardInterrupt:
                print '^C'
                continue
            except EOFError:
                print 'quit'
                break
            finally:
                readline.set_completer()
            if line.startswith('!'):
                os.system(line[1:])
                continue
            elif line in ('quit', 'exit'):
                break
            self.exec_line(line)
