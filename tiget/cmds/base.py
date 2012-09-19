import textwrap
from functools import wraps
from getopt import getopt, GetoptError


commands = {}


class CmdError(Exception): pass


class CmdBase(type):
    def __new__(cls, cls_name, bases, attrs):
        parents = [b for b in bases if isinstance(b, CmdBase)]
        klass = super(CmdBase, cls).__new__(cls, cls_name, bases, attrs)
        if parents:
            commands[klass.name] = klass()
        return klass


class Cmd(object):
    __metaclass__ = CmdBase

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
        return CmdError('{}: {}'.format(self.name, message))

    def argcount_error(self):
        return self.error('wrong number of arguments')

    @property
    def usage(self):
        usage = self.__doc__
        if usage:
            usage = textwrap.dedent(usage).strip()
        return usage

    @classmethod
    def argcount(cls, *counts):
        def _decorator(fn):
            @wraps(fn)
            def _inner(self, opts, args):
                if not len(args) in counts:
                    raise self.argcount_error()
                return fn(self, opts, args)
            return _inner
        return _decorator
