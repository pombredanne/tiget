import re
import textwrap
from functools import wraps
from getopt import getopt, GetoptError


commands = {}
aliases = {}


class CmdError(Exception): pass


class CmdBase(type):
    def __new__(cls, cls_name, bases, attrs):
        parents = [b for b in bases if isinstance(b, CmdBase)]
        klass = super(CmdBase, cls).__new__(cls, cls_name, bases, attrs)
        if parents:
            if not klass.name:
                klass.name = re.match(r'(.*)(?:Cmd)', cls_name).group(1).lower()
            commands[klass.name] = klass()
            aliases.update({k: klass.name for k in klass.aliases})
        return klass


class Cmd(object):
    __metaclass__ = CmdBase

    name = None
    help_text = NotImplemented
    options = ''
    aliases = ()

    def do(self, opts, *args):
        raise NotImplementedError

    def run(self, *argv):
        try:
            opts, args = getopt(argv, self.options)
        except GetoptError as e:
            raise self.error(e)
        try:
            self.do(opts, *args)
        except TypeError:
            raise self.error('wrong number of arguments')

    def error(self, message):
        return CmdError('{}: {}'.format(self.name, message))

    @property
    def usage(self):
        usage = self.__doc__
        if usage:
            usage = textwrap.dedent(usage).strip()
        return usage
