from subprocess import list2cmdline

import tiget
from tiget.conf import settings
from tiget.plugins import plugins
from tiget.cmds import get_command, aliases, cmd, CmdError


@cmd()
def alias_cmd(opts, *args):
    """
    define or list aliases

    SYNOPSIS
        alias ALIAS=CMD ...
    """
    for arg in args:
        try:
            alias, cmd = arg.split('=', 1)
        except ValueError:
            raise CmdError('"=" not found in "{}"'.format(arg))
        aliases[alias] = cmd
    if not args:
        for alias in sorted(aliases.keys()):
            cmd = aliases[alias]
            print('{}={}'.format(alias, list2cmdline([cmd])))


@cmd()
def unalias_cmd(opts, *args):
    """
    remove aliases

    SYNOPSIS
        unalias ALIAS ...
    """
    for alias in args:
        try:
            del aliases[alias]
        except KeyError:
            raise CmdError('no alias named "{}"'.format(alias))


@cmd()
def echo_cmd(opts, *args):
    """
    print text to the screen

    SYNOPSIS
        echo ...
    """
    print(' '.join(args))


@cmd()
def help_cmd(opts, name=None):
    """
    show this help page

    SYNOPSIS
        help [CMD]

    DESCRIPTION
        Print the list of commands when no argument is given.
        Print the usage for CMD otherwise.
    """
    if name:
        try:
            cmd = get_command(name)
        except KeyError:
            raise CmdError('no command named "{}"'.format(name))
        usage = cmd.usage
        if usage:
            print(usage)
        else:
            raise CmdError('no usage information for command "{}"'.format(name))
    else:
        for plugin in plugins.values():
            cmds = list(plugin.cmds.values())
            if not cmds:
                continue
            print('[{}]'.format(plugin.name))
            cmds.sort(key=lambda cmd: cmd.name)
            longest = max(len(cmd.name) for cmd in cmds)
            for cmd in cmds:
                cmd_name = cmd.name.ljust(longest)
                print('{} - {}'.format(cmd_name, cmd.help_text))
            print('')


@cmd()
def set_cmd(opts, *args):
    """
    set configuration variables

    SYNOPSIS
        set
        set [PLUGIN.]VAR=VALUE ...
        set [PLUGIN.][no]VAR ...

    DESCRIPTION
        Print the list of configuration variables when no argument is given.
        String variables can be set with VAR=VALUE. Boolean variables can be
        enabled with VAR and disabled with noVAR.
        Variable names may be prefixed with a module name. If no module name
        is given "core" is assumed.
    """
    for var in args:
        var, eq, value = var.partition('=')
        plugin, _, var = var.rpartition('.')
        if not plugin:
            plugin = 'core'
        if not eq:
            value = True
            if var.startswith('no'):
                var = var[2:]
                value = False
        try:
            settings[plugin][var] = value
        except (ValueError, KeyError) as e:
            raise CmdError(e)
    if not args:
        for plugin in plugins.values():
            if not plugin.settings:
                continue
            print('[{}]'.format(plugin.name))
            for key in sorted(plugin.settings.keys()):
                value = list2cmdline([plugin.settings.get_display(key)])
                print('{}={}'.format(key, value))
            print('')


@cmd()
def source_cmd(opts, filename):
    """
    source configuration file

    SYNOPSIS
        source FILE
    """
    from tiget.script import Script
    try:
        Script.from_file(filename).run()
    except IOError as e:
        raise CmdError(e)


@cmd()
def version_cmd(opts):
    """
    print version information

    SYNOPSIS
        version

    DESCRIPTION
        Print the version. Can be used for version detection in command line
        scripts.
    """
    print(tiget.__version__)
