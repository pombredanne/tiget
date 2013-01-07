import re
from argparse import ArgumentParser


aliases = {
    'man': 'help',
    '.': 'source',
    'ls': 'list',
}


class CmdError(Exception): pass


class CmdExit(Exception):
    def __init__(self, status=None):
        super().__init__()
        self.status = status


class CmdArgumentParser(ArgumentParser):
    def __init__(self, cmd):
        super().__init__(prog=cmd.name, description=cmd.description)
        self.cmd = cmd

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message)
        raise CmdExit(status)

    def error(self, message):
        raise self.cmd.error(message)


class CmdBase(type):
    def __new__(cls, cls_name, bases, attrs):
        parents = [b for b in bases if isinstance(b, CmdBase)]
        if parents:
            attrs.setdefault('name', cls_name.lower())
        return super().__new__(cls, cls_name, bases, attrs)


class Cmd(metaclass=CmdBase):
    description = 'undocumented'

    def __init__(self):
        self.parser = CmdArgumentParser(self)
        self.setup()

    def setup(self):
        pass

    def format_help(self):
        return self.parser.format_help()

    def run(self, *argv):
        try:
            args = self.parser.parse_args(argv)
            self.do(args)
        except CmdExit:
            return

    def error(self, message):
        return CmdError('{}: {}'.format(self.name, message))

    def do(self, args):
        raise NotImplementedError
