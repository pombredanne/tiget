from tiget.git.models.base import Model
from tiget.git.models.fields import *
from tiget.git.models.query import Q


def get_model(name):
    from tiget.plugins import plugins
    for plugin in plugins.values():
        try:
            return plugin.models[name.lower()]
        except KeyError:
            pass
    raise KeyError(name)
