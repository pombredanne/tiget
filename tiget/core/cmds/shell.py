from subprocess import list2cmdline

import tiget
from tiget.conf import settings
from tiget.plugins import plugins
from tiget.cmds import get_command, aliases, Cmd
from tiget.utils import paginate


__all__ = ['Alias', 'Unalias', 'Echo', 'Help', 'Set', 'Source', 'Version']


class Alias(Cmd):
    description = 'define or list aliases'

    def setup(self):
        self.parser.add_argument('args', nargs='*')

    def do(self, args):
        for arg in args.args:
            try:
                alias, cmd = arg.split('=', 1)
            except ValueError:
                raise self.error('"=" not found in "{}"'.format(arg))
            aliases[alias] = cmd
        if not args.args:
            for alias in sorted(aliases.keys()):
                cmd = aliases[alias]
                print('{}={}'.format(alias, list2cmdline([cmd])))


class Unalias(Cmd):
    description = 'remove aliases'

    def setup(self):
        self.parser.add_argument('args', nargs='*')

    def do(self, args):
        for alias in args.args:
            try:
                del aliases[alias]
            except KeyError:
                raise self.error('no alias named "{}"'.format(alias))


class Echo(Cmd):
    description = 'print text to the screen'

    def setup(self):
        self.parser.add_argument('args', nargs='*')

    def do(self, args):
        print(' '.join(args.args))


class Help(Cmd):
    description = 'show this help message'

    def setup(self):
        self.parser.add_argument('name', nargs='?')
        self.parser.epilog = '''
            Print the usage for a command when a name is given on the command
            line, otherwise print the list of commands.
        '''

    def do(self, args):
        if args.name:
            try:
                cmd = get_command(args.name)
            except KeyError:
                raise self.error('no command named "{}"'.format(args.name))
            paginate(cmd.format_help())
        else:
            for plugin in sorted(plugins.values(), key=lambda p: p.name):
                cmds = list(plugin.cmds.values())
                if not cmds:
                    continue
                print('[{}]'.format(plugin.name))
                longest = max(len(cmd.name) for cmd in cmds)
                for cmd in sorted(cmds, key=lambda cmd: cmd.name):
                    cmd_name = cmd.name.ljust(longest)
                    print('{} - {}'.format(cmd_name, cmd.description))
                print('')


class Set(Cmd):
    description = 'set configuration variables'

    def setup(self):
        self.parser.add_argument('args', nargs='*')
        self.parser.epilog = '''
            Print the list of configuration variables when no argument is given.
            String variables can be set with VAR=VALUE. Boolean variables can be
            enabled with VAR and disabled with noVAR.
            Variable names may be prefixed with a module name. If no module name
            is given "core" is assumed.
        '''

    def do(self, args):
        for var in args.args:
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
                raise self.error(e)
        if not args.args:
            for plugin in sorted(plugins.values(), key=lambda p: p.name):
                if not plugin.settings:
                    continue
                print('[{}]'.format(plugin.name))
                for key in sorted(plugin.settings.keys()):
                    value = list2cmdline([plugin.settings.get_display(key)])
                    print('{}={}'.format(key, value))
                print('')


class Source(Cmd):
    description = 'source configuration file'

    def setup(self):
        self.parser.add_argument('filename')

    def do(self, args):
        from tiget.script import Script
        try:
            script = Script.from_file(args.filename)
        except IOError as e:
            raise self.error(e)
        script.run()


class Version(Cmd):
    description = 'print version information'

    def setup(self):
        self.parser.epilog = '''
            Print the version. Can be used for version detection in command
            line scripts.
        '''

    def do(self, args):
        print(tiget.__version__)
