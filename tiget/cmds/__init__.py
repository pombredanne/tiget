import os
import shlex

from tiget.cmds.base import aliases, CmdError, Cmd
from tiget.plugins import plugins


def get_command(name):
    for plugin in plugins.values():
        try:
            cmd = plugin.cmds[name]
            break
        except KeyError:
            pass
    else:
        raise KeyError(name)
    return cmd


def cmd_execv(argv):
    if argv[0] in aliases:
        argv = shlex.split(aliases[argv[0]]) + argv[1:]
    name = argv.pop(0)
    try:
        cmd = get_command(name)
    except KeyError:
        raise CmdError('{}: command not found'.format(name))
    cmd.run(*argv)


def cmd_exec(line):
    if not line or line.startswith('#'):
        pass
    elif line.startswith('!'):
        status = os.system(line[1:])
        if status:
            raise CmdError(
                'shell returned with exit status {}'.format(status % 255))
    elif line.startswith('%'):
        ns = {}
        for plugin in plugins.values():
            models = plugin.models
            ns.update({model.__name__: model for model in models.values()})
        code = compile(line[1:], '<exec>', 'single')
        exec(code, ns)
    else:
        try:
            line = shlex.split(line)
        except ValueError as e:
            raise CmdError(e)
        cmd_execv(line)


def cmd_execfile(f):
    for lineno, line in enumerate(f.readlines(), 1):
        line = line.strip()
        if line in ('quit', 'exit'):
            break
        try:
            cmd_exec(line)
        except CmdError as e:
            raise CmdError('"{}", line {}: {}'.format(f.name, lineno, e))
