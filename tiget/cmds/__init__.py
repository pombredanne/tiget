import shlex

from tiget.cmds.base import aliases, CmdError, cmd, Cmd


def get_command(name):
    from tiget.plugins import plugins
    for plugin in plugins.values():
        try:
            cmd = plugin.cmds[name]
            break
        except KeyError:
            pass
    else:
        raise KeyError(name)
    return cmd


def run(argv):
    if argv[0] in aliases:
        argv = shlex.split(aliases[argv[0]]) + argv[1:]
    name = argv.pop(0)
    try:
        cmd = get_command(name)
    except KeyError:
        raise CmdError('{}: command not found'.format(name))
    cmd(*argv)
