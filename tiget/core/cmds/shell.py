from subprocess import list2cmdline

from tiget.conf import settings
from tiget.plugins import plugins
from tiget.cmds import get_command, aliases, Cmd
from tiget.cmds.types import dict_type
from tiget.utils import open_in_editor
from tiget.git import transaction, GitError


__all__ = ['Alias', 'Unalias', 'Echo', 'EditConfig', 'Help', 'Set', 'Source']


class Alias(Cmd):
    description = 'define or list aliases'

    def setup(self):
        self.parser.add_argument('aliases', nargs='*', type=dict_type)

    def do(self, args):
        aliases.update(args.aliases)
        if not args.aliases:
            for alias in sorted(aliases.keys()):
                cmd = aliases[alias]
                self.print('{}={}'.format(alias, list2cmdline([cmd])))


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
        self.print(*args.args)


class EditConfig(Cmd):
    description = 'edit a file located in the repository'

    def setup(self):
        self.parser.add_argument('-c', '--create', action='store_true')
        self.parser.add_argument('filename', nargs='?', default='tigetrc')

    @transaction.wrap()
    def do(self, args):
        path = args.filename.lstrip('/').split('/')
        if not args.filename.startswith('/'):
            path.insert(0, 'config')
        try:
            trans = transaction.current()
        except GitError as e:
            raise self.error(e)
        try:
            current_content = trans.get_blob(path).decode('utf-8')
        except GitError as e:
            if args.create:
                current_content = ''
            else:
                raise self.error(e)
        new_content = open_in_editor(current_content)
        trans.set_blob(path, new_content.encode('utf-8'))
        if new_content == current_content:
            raise self.error('nothing changed')
        trans.add_message('Changed {}'.format(args.filename))


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
            self.print(cmd.format_help())
        else:
            for plugin in sorted(plugins.values(), key=lambda p: p.name):
                cmds = list(plugin.cmds.values())
                if not cmds:
                    continue
                self.print('[{}]'.format(plugin.name))
                longest = max(len(cmd.name) for cmd in cmds)
                for cmd in sorted(cmds, key=lambda cmd: cmd.name):
                    cmd_name = cmd.name.ljust(longest)
                    self.print('{} - {}'.format(cmd_name, cmd.description))
                self.print()


class Set(Cmd):
    description = 'set configuration variables'

    def setup(self):
        self.parser.add_argument('args', nargs='*')
        self.parser.epilog = '''
            Print the list of configuration variables when no argument is
            given. String variables can be set with VAR=VALUE. Boolean
            variables can be enabled with VAR and disabled with noVAR.
            Variable names may be prefixed with a module name. If no module
            name is given "core" is assumed.
        '''

    def do(self, args):
        for var in args.args:
            try:
                settings.parse_and_set(var)
            except (ValueError, KeyError) as e:
                raise self.error(e)
        if not args.args:
            for plugin in sorted(plugins.values(), key=lambda p: p.name):
                if not plugin.settings:
                    continue
                self.print('[{}]'.format(plugin.name))
                for key in sorted(plugin.settings.keys()):
                    value = list2cmdline([plugin.settings.get_display(key)])
                    self.print('{}={}'.format(key, value))
                self.print()


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
