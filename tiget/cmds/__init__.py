import shlex

from tiget.cmds.base import commands, aliases, Cmd, CmdError
from tiget.cmds import builtins
from tiget.cmds import transaction
from tiget.cmds import ticket
from tiget.cmds import model

def run(argv):
    if argv[0] in aliases:
        argv = shlex.split(aliases[argv[0]]) + argv[1:]
    name = argv.pop(0)
    try:
        cmd = commands[name]
    except KeyError:
        raise CmdError('{}: command not found'.format(name))
    cmd.run(*argv)
