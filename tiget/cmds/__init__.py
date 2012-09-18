from tiget.cmds import builtins
from tiget.cmds import transaction
from tiget.cmds import ticket
from tiget.cmds.base import commands, CmdError

def run(argv):
    name = argv.pop(0)
    try:
        cmd = commands[name]
    except KeyError:
        raise CmdError('{0}: command not found'.format(name))
    cmd.run(*argv)
