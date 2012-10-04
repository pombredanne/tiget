import pkg_resources
from collections import OrderedDict
from inspect import ismodule, isclass

from tiget.deep_reload import deep_reload


plugins = OrderedDict()


class Plugin(object):
    def __init__(self, mod, name):
        self.mod = mod
        self.name = name
        self.load()

    def load(self):
        self.models = {}
        self.cmds = {}
        self.settings = Settings()
        try:
            init_plugin = self.mod.init_plugin
        except AttributeError:
            pass
        else:
            init_plugin(self)

    def unload(self):
        try:
            del_plugin = self.mod.del_plugin
        except AttributeError:
            pass
        else:
            del_plugin(self)

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
        from tiget.models import Model
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


class Settings(object):
    def __init__(self):
        self.variables = {}
        self.data = {}

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key, value):
        if key in ('variables', 'data') or not key in self:
            super(Settings, self).__setattr__(key, value)
        else:
            self[key] = value

    def __getitem__(self, key):
        try:
            variable = self.variables[key]
        except KeyError:
            raise KeyError('invalid setting "{}"'.format(key))
        if not key in self.data:
            return variable.default
        return self.data[key]

    def __setitem__(self, key, value):
        try:
            variable = self.variables[key]
        except KeyError:
            raise KeyError('invalid setting "{}"'.format(key))
        variable.validate(value)
        self.data[key] = value

    def __len__(self):
        return len(self.variables)

    def __contains__(self, key):
        return key in self.variables

    def keys(self):
        return self.variables.keys()


def load_plugin(name):
    for ep in pkg_resources.iter_entry_points('tiget.plugins', name):
        mod = ep.load()
        name = ep.name
        break
    else:
        mod = __import__(name, fromlist=['__name__'])
        name = mod.__name__.rpartition('.')[2]
    plugins[name] = Plugin(mod, name)


def unload_plugin(name):
    plugin = plugins.pop(name)
    plugin.unload()


def reload_plugin(name):
    plugin = plugins[name]
    plugin.unload()
    plugin.load()
