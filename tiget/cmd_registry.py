import textwrap
from getopt import getopt, GetoptError

class CmdError(Exception):
    pass

class Cmd(object):
    name = NotImplemented
    help_text = NotImplemented
    options = ''

    def do(self, opts, args):
        raise NotImplementedError

    def run(self, *argv):
        try:
            opts, args = getopt(argv, self.options)
        except GetoptError as e:
            raise self.error(e)
        self.do(opts, args)

    def error(self, message):
        return CmdError('{0}: {1}'.format(self.name, message))

    def argcount_error(self):
        return self.error('wrong number of arguments')

    @property
    def usage(self):
        usage = self.__doc__
        if usage:
            usage = textwrap.dedent(usage).strip()
        return usage

class CmdRegistry(dict):
    def add(self, klass):
        self[klass.name] = klass()

    def run(self, argv):
        name = argv.pop(0)
        try:
            cmd = self[name]
        except KeyError:
            raise CmdError('{0}: command not found'.format(name))
        cmd.run(*argv)

cmd_registry = CmdRegistry()
