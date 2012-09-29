import pkg_resources
from collections import OrderedDict
from inspect import ismodule, isclass

from tiget.models import Model
from tiget.cmds import Cmd


plugins = OrderedDict()


class Plugin(object):
    def __init__(self, mod):
        self.mod = mod
        self.models = {}
        self.cmds = {}
        self.settings = {}
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

    def add_models(self, models):
        if ismodule(models):
            for k, v in models.__dict__.iteritems():
                if not k.startswith('_') and isclass(v) and issubclass(v, Model):
                    self.add_model(v)
        else:
            for model in models:
                self.add_model(model)

    def add_model(self, model):
        self.models[model.__name__.lower()] = model

    def add_cmds(self, cmds):
        if ismodule(cmds):
            for k, v in cmds.__dict__.iteritems():
                if not k.startswith('_') and isinstance(v, Cmd):
                    self.add_cmd(v)
        else:
            for cmd in cmds:
                self.add_cmd(cmd)

    def add_cmd(self, cmd):
        self.cmds[cmd.name] = cmd


def load_plugin(plugin_name):
    for ep in pkg_resources.iter_entry_points('tiget.plugins', plugin_name):
        mod = ep.load()
        break
    else:
        mod = __import__(plugin_name, fromlist=['__name__'])

    plugin = Plugin(mod)
    plugins[plugin.name] = plugin
