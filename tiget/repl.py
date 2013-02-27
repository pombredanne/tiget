import os
import sys
import readline

from colors import blue

from tiget.version import VERSION
from tiget.conf import settings
from tiget.plugins import plugins
from tiget.cmds import CmdError, aliases, cmd_exec
from tiget.utils import print_error, post_mortem


class Repl:
    def __init__(self):
        self.instream = sys.stdin
        self.infile = '<repl>'
        self.lineno = 0

    def complete(self, text, state):
        cmds = set(aliases.keys())
        for plugin in plugins.values():
            cmds.update(plugin.cmds.keys())
        options = list(sorted(cmd for cmd in cmds if cmd.startswith(text)))
        if state < len(options):
            return options[state] + ' '
        return None

    def readline(self):
        prompt = 'tiget[{}]% '.format(self.lineno)
        if settings.core.color:
            prompt = blue(prompt)
        readline.set_completer(self.complete)
        try:
            line = input(prompt).strip()
        except KeyboardInterrupt:
            print('^C')
            raise
        except EOFError:
            print('quit')
            raise
        finally:
            readline.set_completer()
        if not line:
            self.lineno -= 1
        return line

    @property
    def histfile(self):
        return os.path.expanduser(settings.core.history_file)

    def print_error(self, e):
        print_error('"{}", line {}: {}'.format(self.infile, self.lineno, e))

    def run(self):
        print('tiget {}'.format(VERSION))
        print('Type "help" for help')
        print('')
        readline.parse_and_bind('tab: complete')
        try:
            readline.read_history_file(self.histfile)
        except IOError:
            pass        # The file might not exist yet
        while True:
            self.lineno += 1
            try:
                line = self.readline()
                if line in ('quit', 'exit'):
                    raise EOFError(line)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            try:
                cmd_exec(line)
            except CmdError as e:
                self.print_error(e)
            except:
                self.print_error('internal error (see traceback)')
                post_mortem()
        readline.set_history_length(settings.core.history_limit)
        readline.write_history_file(self.histfile)
