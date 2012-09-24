import os
import sys
import readline
import shlex
import traceback
from StringIO import StringIO

from colors import green

from tiget import get_version, aliases
from tiget.settings import settings
from tiget.cmds import commands, CmdError, run
from tiget.utils import print_error


class Script(object):
    def __init__(self, instream, infile, ignore_errors=False):
        if isinstance(instream, basestring):
            instream = StringIO(instream)
        self.instream = instream
        self.infile = infile
        self.ignore_errors = ignore_errors
        self.lineno = 0

    def print_error(self, e):
        print_error('"{}", line {}: {}'.format(self.infile, self.lineno, e))

    def readline(self):
        line = self.instream.readline()
        if not line:
            raise EOFError()
        return line.strip()

    def run_line(self, line):
        try:
            line = shlex.split(line)
        except ValueError as e:
            raise CmdError(e)
        run(line)

    def run(self):
        while True:
            self.lineno += 1
            try:
                line = self.readline()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            if not line:
                continue
            elif line.startswith('!'):
                os.system(line[1:])
                continue
            elif line in ('quit', 'exit'):
                break
            try:
                self.run_line(line)
            except CmdError as e:
                self.print_error(e)
                if not self.ignore_errors:
                    return 1
            except Exception:
                traceback.print_exc()
                self.print_error('internal error (see traceback)')
                if not self.ignore_errors:
                    return 1


class Repl(Script):
    def __init__(self):
        super(Repl, self).__init__(sys.stdin, '<repl>', ignore_errors=True)

    def complete(self, text, state):
        cmds = commands.keys() + aliases.keys()
        options = [cmd for cmd in cmds if cmd.startswith(text)]
        if state < len(options):
            return options[state] + ' '
        return None

    def readline(self):
        prompt = 'tiget[{}]% '.format(self.lineno)
        if settings.color:
            prompt = green(prompt)
        readline.set_completer(self.complete)
        try:
            line = raw_input(prompt).strip()
        except KeyboardInterrupt:
            print '^C'
            raise
        except EOFError:
            print 'quit'
            raise
        finally:
            readline.set_completer()
        if not line:
            self.lineno -= 1
        return line

    def run(self):
        print 'tiget {}'.format(get_version())
        print 'Type "help" for help'
        print ''
        readline.parse_and_bind('tab: complete')
        super(Repl, self).run()
