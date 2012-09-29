import pipes

import tiget
from tiget.settings import settings
from tiget.cmds.base import commands, aliases, Cmd
from tiget.utils import create_module, post_mortem, load_file
from tiget.plugins import load_plugin


class AliasCmd(Cmd):
    """
    usage: alias ALIAS=CMD ...
    """
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
    help_text = 'remove aliases'

    def do(self, opts, *args):
        for alias in args:
            try:
                del aliases[alias]
            except KeyError:
                raise self.error('no alias named "{}"'.format(alias))


class EchoCmd(Cmd):
    """
    usage: echo ...
    """
    help_text = 'print text to the screen'

    def do(self, opts, *args):
        print ' '.join(args)


class HelpCmd(Cmd):
    """
    usage: help [CMD]

    Print the list of commands when no argument is given.
    Print the usage for CMD otherwise.
    """
    help_text = 'show this help page'

    def do(self, opts, name=None):
        if name:
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
        else:
            cmds = commands.values()
            cmds.sort(key=lambda cmd: cmd.name)
            longest = max(len(cmd.name) for cmd in cmds)
            for cmd in cmds:
                cmd_name = cmd.name.ljust(longest)
                print '{} - {}'.format(cmd_name, cmd.help_text)


class LoadConfigCmd(Cmd):
    """
    usage: load-config NAME FILE
    """
    name = 'load-config'
    help_text = 'load python configuration file'

    def do(self, opts, name, filename):
        import config
        try:
            content = load_file(filename) + '\n'
        except IOError as e:
            raise self.error(e)
        m = create_module('.'.join([config.__name__, name]))
        setattr(config, name, m)
        m.__file__ = filename
        code = compile(content, filename, 'exec')
        exec(code, m.__dict__)


class LoadPluginCmd(Cmd):
    """
    usage: load-plugin PLUGIN
    """
    name = 'load-plugin'
    help_text = 'load plugin'

    def do(self, opts, plugin_name):
        try:
            load_plugin(plugin_name)
        except KeyError:
            raise self.error('plugin "{}" not found'.format(plugin_name))


class SetCmd(Cmd):
    """
    usage: set [VAR=VALUE [...]]

    Print the list of configuration variables when no argument is given.
    String variables can be set with VAR=VALUE. Boolean variables can be
    enabled with VAR and disabled with noVAR.
    """
    help_text = 'set variable VAR to VALUE'

    def do(self, opts, *args):
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


class SourceCmd(Cmd):
    """
    usage: source FILE
    """
    help_text = 'source config file'

    def do(self, opts, filename):
        from tiget.script import Script
        try:
            Script.from_file(filename).run()
        except IOError as e:
            raise self.error(e)


class VersionCmd(Cmd):
    """
    usage: version

    Print the version. Can be used for version detection in command line
    scripts.
    """
    help_text = 'print version information'

    def do(self, opts):
        print tiget.__version__
