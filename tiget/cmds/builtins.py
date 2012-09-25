import pipes
from tiget import get_version
from tiget.settings import settings
from tiget.cmds.base import commands, aliases, Cmd


class AliasCmd(Cmd):
    """
    usage: alias ALIAS=CMD ...
    """
    name = 'alias'
    help_text = 'define or list aliases'

    def do(self, opts, *args):
        for arg in args:
            try:
                alias, cmd = arg.split('=', 1)
            except ValueError:
                raise self.error('"=" not found in "{}"'.format(arg))
            aliases[alias] = cmd
        if not args:
            for alias in sorted(aliases.keys()):
                cmd = aliases[alias]
                print '{}: {}'.format(alias, cmd)


class UnaliasCmd(Cmd):
    """
    usage: unalias ALIAS ...
    """
    name = 'unalias'
    help_text = 'remove aliases'

    def do(self, opts, *args):
        for alias in args:
            try:
                del aliases[alias]
            except KeyError:
                raise self.error('no alias named "{}"'.format(alias))


class HelpCmd(Cmd):
    """
    usage: help [CMD]

    Print the list of commands when no argument is given.
    Print the usage for <cmd> otherwise.
    """
    name = 'help'
    help_text = 'show this help page'
    aliases = ('?', 'man')

    def do(self, opts, name=None):
        if name is None:
            cmds = commands.values()
            cmds.sort(key=lambda cmd: cmd.name)
            longest = max(len(cmd.name) for cmd in cmds)
            for cmd in cmds:
                cmd_name = cmd.name.ljust(longest)
                print '{} - {}'.format(cmd_name, cmd.help_text)
        else:
            try:
                cmd = commands[name]
            except KeyError:
                raise self.error('no command named "{}"'.format(name))
            usage = cmd.usage
            if usage:
                print usage
            else:
                raise self.error(
                    'no usage information for command "{}"'.format(name))


class SetCmd(Cmd):
    """
    usage: set [VAR=VALUE [...]]

    Print the list of configuration variables when no argument is given.
    String variables can be set with VAR=VALUE. Boolean variables can be
    enabled with VAR and disabled with noVAR.
    """
    name = 'set'
    help_text = 'set variable VAR to VALUE'

    def do(self, opts, *args):
        for var in args:
            try:
                var, value = var.split('=', 1)
            except ValueError:
                if var.startswith('no'):
                    settings[var[2:]] = False
                else:
                    settings[var] = True
            else:
                try:
                    settings[var] = value
                except ValueError as e:
                    raise self.error(e)
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


class VersionCmd(Cmd):
    """
    usage: version

    Print the version. Can be used for version detection in command line
    scripts.
    """
    name = 'version'
    help_text = 'print version information'

    def do(self, opts):
        print get_version()
