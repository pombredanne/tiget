import os
import sys
import readline
import shlex
import traceback

from colors import red, green

from tiget import settings, get_version
from tiget.cmds import commands, CmdError, run


class Repl(object):
    def complete(self, text, state):
        cmds = commands.keys() + settings.aliases.keys()
        options = [cmd for cmd in cmds if cmd.startswith(text)]
        if state < len(options):
            return options[state] + ' '
        return None

    def print_error(self, line):
        if settings.use_color and sys.stderr.isatty():
            line = red(line)
        print >> sys.stderr, line

    def run(self):
        print 'tiget {0}'.format(get_version())
        print 'Type "help" for help.'
        print ''
        readline.parse_and_bind('tab: complete')
        while True:
            prompt = 'tiget% '
            if settings.use_color and sys.stdout.isatty():
                prompt = green(prompt)
            readline.set_completer(self.complete)
            try:
                line = raw_input(prompt).lstrip()
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
            try:
                line = shlex.split(line)
            except ValueError as e:
                self.print_error('Syntax error: {0}'.format(e))
                continue
            if line:
                if line[0] in settings.aliases:
                    line = shlex.split(settings.aliases[line[0]]) + line[1:]
                if line[0] == 'quit':
                    break
                try:
                    run(line)
                except CmdError as e:
                    self.print_error(str(e))
                except Exception:
                    traceback.print_exc()
