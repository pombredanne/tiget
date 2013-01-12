import pkg_resources

from tiget.cmds import Cmd
from tiget.plugins import load_plugin, unload_plugin, reload_plugin, plugins


__all__ = ['Load', 'Reload', 'Unload']


class Load(Cmd):
    description = 'load plugin'

    def setup(self):
        self.parser.add_argument('plugin_name', nargs='?')

    def do(self, args):
        if args.plugin_name:
            try:
                load_plugin(args.plugin_name)
            except ImportError as e:
                raise self.error(e)
        else:
            self.print('Available plugins:')
            names = set(
                ep.name for ep in pkg_resources.iter_entry_points('tiget.plugins'))
            names.update(plugins.keys())
            for name in sorted(names):
                loaded = name in plugins
                self.print('[{}] {}'.format('*' if loaded else ' ', name))


class Reload(Cmd):
    description = 'reload plugin'

    def setup(self):
        self.parser.add_argument('plugin_name')

    def do(self, args):
        try:
            reload_plugin(args.plugin_name)
        except KeyError:
            raise self.error('no plugin "{}" loaded'.format(args.plugin_name))


class Unload(Cmd):
    description = 'unload plugin'

    def setup(self):
        self.parser.add_argument('plugin_name')

    def do(self, args):
        try:
            unload_plugin(args.plugin_name)
        except KeyError:
            raise self.error('no plugin "{}" loaded'.format(args.plugin_name))
