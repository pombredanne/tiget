import pkg_resources


plugins = {}


class Plugin(object):
    def __init__(self, mod):
        self.mod = mod
        try:
            init_plugin = mod.init_plugin
        except AttributeError:
            pass
        else:
            init_plugin(self)

    def __del__(self):
        try:
            del_plugin = self.mod.del_plugin
        except AttributeError:
            pass
        else:
            del_plugin(self)

    def reload(self):
        self.__del__()
        mod = reload(self.mod)
        self.__init__(mod)

    @property
    def name(self):
        return self.mod.__name__.rpartition('.')[2]

    @property
    def author(self):
        return getattr(self.mod, '__author__', None)

    @property
    def version(self):
        return getattr(self.mod, '__version__', None)


def load_plugin(plugin_name):
    for ep in pkg_resources.iter_entry_points('tiget.plugins', plugin_name):
        mod = ep.load()
        break
    else:
        mod = __import__(plugin_name, fromlist=['__name__'])

    plugin = Plugin(mod)
    plugins[plugin.name] = plugin
