import pkg_resources
from collections import OrderedDict
from inspect import ismodule, isclass

from tiget.plugins.deep_reload import deep_reload
from tiget.plugins.settings import Settings


plugins = OrderedDict()


def _get_subclasses(mod, klass):
    all_ = getattr(mod, '__all__', vars(mod).keys())
    for key in all_:
        value = vars(mod)[key]
        if key.startswith('_') or value == klass:
            continue
        if isclass(value) and issubclass(value, klass):
            yield value


class Plugin:
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

    def add_models(self, models):
        from git_orm.models import Model
        if ismodule(models):
            models = _get_subclasses(models, Model)
        for model in models:
            self.add_model(model)

    def add_model(self, model):
        self.models[model.__name__.lower()] = model

    def add_cmds(self, cmds):
        from tiget.cmds import Cmd
        if ismodule(cmds):
            cmds = _get_subclasses(cmds, Cmd)
        for cmd in cmds:
            if not cmd.abstract:
                self.add_cmd(cmd)

    def add_cmd(self, cmd_class):
        for name in cmd_class.names:
            self.cmds[name] = cmd_class(name)

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
