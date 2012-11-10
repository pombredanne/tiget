import pkg_resources
from collections import OrderedDict
from inspect import ismodule, isclass

from tiget.plugins.deep_reload import deep_reload
from tiget.plugins.settings import Settings


plugins = OrderedDict()


class Plugin(object):
    def __init__(self, mod, name):
        self.mod = mod
        self.name = name

    def load(self):
        self.models = {}
        self.cmds = {}
        self.settings = Settings()
        try:
            load = self.mod.load
        except AttributeError:
            pass
        else:
            load(self)

    def unload(self):
        try:
            unload = self.mod.unload
        except AttributeError:
            pass
        else:
            unload(self)

    def reload(self):
        self.unload()
        self.mod = deep_reload(self.mod)
        self.load()

    @property
    def author(self):
        return getattr(self.mod, '__author__', None)

    @property
    def version(self):
        return getattr(self.mod, '__version__', None)

    def add_models(self, models):
        from tiget.git.models import Model
        if ismodule(models):
            for k, v in models.__dict__.items():
                if not k.startswith('_') and isclass(v) and issubclass(v, Model):
                    self.add_model(v)
        else:
            for model in models:
                self.add_model(model)

    def add_model(self, model):
        self.models[model.__name__.lower()] = model

    def add_cmds(self, cmds):
        from tiget.cmds import Cmd
        if ismodule(cmds):
            for k, v in cmds.__dict__.items():
                if not k.startswith('_') and isinstance(v, Cmd):
                    self.add_cmd(v)
        else:
            for cmd in cmds:
                self.add_cmd(cmd)

    def add_cmd(self, cmd):
        self.cmds[cmd.name] = cmd

    def add_settings(self, **kwargs):
        for name, variable in kwargs.items():
            self.add_setting(name, variable)

    def add_setting(self, name, variable):
        self.settings.variables[name] = variable


def load_plugin(name):
    for ep in pkg_resources.iter_entry_points('tiget.plugins', name):
        mod = ep.load()
        name = ep.name
        break
    else:
        mod = __import__(name, fromlist=['__name__'])
        name = mod.__name__.rpartition('.')[2]
    if name in plugins:
        raise ImportError('plugin "{}" is already loaded'.format(name))
    plugin = Plugin(mod, name)
    plugins[name] = plugin
    plugin.load()


def unload_plugin(name):
    plugin = plugins.pop(name)
    plugin.unload()


def reload_plugin(name):
    plugin = plugins[name]
    plugin.reload()
