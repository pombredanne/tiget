import pipes

import tiget
from tiget.settings import settings
from tiget.cmds import commands, aliases, cmd, CmdError


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
            print '{}: {}'.format(alias, cmd)


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
    print ' '.join(args)


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
            cmd = commands[name]
        except KeyError:
            raise CmdError('no command named "{}"'.format(name))
        usage = cmd.usage
        if usage:
            print usage
        else:
            raise CmdError('no usage information for command "{}"'.format(name))
    else:
        cmds = commands.values()
        cmds.sort(key=lambda cmd: cmd.name)
        longest = max(len(cmd.name) for cmd in cmds)
        for cmd in cmds:
            cmd_name = cmd.name.ljust(longest)
            print '{} - {}'.format(cmd_name, cmd.help_text)


@cmd()
def set_cmd(opts, *args):
    """
    set configuration variables

    SYNOPSIS
        set VAR=VALUE ...
        set [no]VAR ...

    DESCRIPTION
        Print the list of configuration variables when no argument is given.
        String variables can be set with VAR=VALUE. Boolean variables can be
        enabled with VAR and disabled with noVAR.
    """
    for var in args:
        try:
            var, value = var.split('=', 1)
        except ValueError:
            if var.startswith('no'):
                var = var[2:]
                value = False
            else:
                value = True
        try:
            settings[var] = value
        except (ValueError, KeyError) as e:
            raise CmdError(e)
    if not args:
        for key in sorted(settings.keys()):
            value = settings[key]
            if value is True:
                value = 'on'
            elif value is False:
                value = 'off'
            else:
                value = pipes.quote(value)
            print '{}: {}'.format(key, value)


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
    print tiget.__version__
