from tiget.plugins import plugins


def model_type(name):
    for plugin in plugins.values():
        try:
            return plugin.models[name.lower()]
        except KeyError:
            pass
    raise TypeError


def dict_type(arg):
    try:
        key, value = arg.split('=', 1)
    except ValueError:
        raise TypeError('"=" not found in "{}"'.format(arg))
    return (key, value)
