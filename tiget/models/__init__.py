from tiget.models.base import Model
from tiget.models.fields import *


def get_model(name):
    from tiget.plugins import plugins
    for plugin in plugins.values():
        try:
            model = plugin.models[name.lower()]
            break
        except KeyError:
            pass
    else:
        raise KeyError(name)
    return model
