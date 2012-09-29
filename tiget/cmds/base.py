import re
import textwrap
from functools import wraps
from getopt import getopt, GetoptError


commands = {}
aliases = {}


class CmdError(Exception): pass


def get_cmd_name(name):
    m = re.match(r'(.*?)(?:_?cmd)?$', name, re.IGNORECASE)
    return m.group(1).replace('_', '-').lower()


def cmd(**kwargs):
    def _decorator(fn):
        cmd = Cmd(fn, **kwargs)
        commands[cmd.name] = cmd
        return wraps(fn)(cmd)
    return _decorator


class Cmd(object):
    def __init__(self, fn, name=None, options=''):
        self.fn = fn
        if not name:
            name = get_cmd_name(fn.__name__)
        self.name = name
        self.options = options

    def __call__(self, *argv):
        try:
            opts, args = getopt(argv, self.options)
        except GetoptError as e:
            raise self.error(e)
        try:
            self.fn(opts, *args)
        except TypeError:
            raise CmdError('{}: wrong number of arguments'.format(self.name))
        except CmdError as e:
            raise CmdError('{}: {}'.format(self.name, e))

    @property
    def usage(self):
        usage = self.fn.__doc__
        if usage:
            usage = self.name + ' - ' + textwrap.dedent(usage).strip()
        return usage

    @property
    def help_text(self):
        help_text = 'undocumented'
        if self.fn.__doc__:
            help_text = self.fn.__doc__.strip().splitlines()[0]
        return help_text
