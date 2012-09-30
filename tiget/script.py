import os
import sys
import readline
import shlex
from StringIO import StringIO

from colors import green

import tiget
from tiget.settings import settings
from tiget.plugins import plugins
from tiget.cmds import aliases, CmdError, run
from tiget.utils import print_error, post_mortem, load_file


class Script(object):
    def __init__(self, instream, infile, ignore_errors=False):
        if isinstance(instream, basestring):
            instream = StringIO(instream)
        self.instream = instream
        self.infile = infile
        self.ignore_errors = ignore_errors
        self.lineno = 0

    @classmethod
    def from_file(cls, f):
        if isinstance(f, basestring):
            name = f
            f = load_file(f)
        else:
            name = f.name
        return cls(f, name)

    def print_error(self, e):
        print_error('"{}", line {}: {}'.format(self.infile, self.lineno, e))

    def readline(self):
        line = self.instream.readline()
        if not line:
            raise EOFError()
        return line.strip()

    def run_line(self, line):
        if not line or line.startswith('#'):
            pass
        elif line.startswith('!'):
            status = os.system(line[1:])
            if status:
                raise CmdError(
                    'shell returned with exit status {}'.format(status % 255))
        elif line.startswith('%'):
            code = compile(line[1:], self.infile, 'single')
            exec(code, {})
        else:
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
                if line in ('quit', 'exit'):
                    raise EOFError(line)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            try:
                self.run_line(line)
            except CmdError as e:
                self.print_error(e)
                if not self.ignore_errors:
                    return 1
            except:
                self.print_error('internal error (see traceback)')
                post_mortem()
                if not self.ignore_errors:
                    return 1


class Repl(Script):
    def __init__(self):
        super(Repl, self).__init__(sys.stdin, '<repl>', ignore_errors=True)

    def complete(self, text, state):
        cmds = []
        for plugin in plugins.itervalues():
            cmds += plugin.cmds.keys()
        cmds += aliases.keys()
        options = [cmd for cmd in cmds if cmd.startswith(text)]
        if state < len(options):
            return options[state] + ' '
        return None

    def readline(self):
        prompt = 'tiget[{}]% '.format(self.lineno)
        if settings.core.color:
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
        print 'tiget {}'.format(tiget.__version__)
        print 'Type "help" for help'
        print ''
        readline.parse_and_bind('tab: complete')
        super(Repl, self).run()
