import sys
from imp import reload, is_builtin
from inspect import ismodule


def _is_in_tiget(mod):
    if 'tiget' in (mod.__name__, mod.__package__):
        return True
    elif mod.__package__ and mod.__package__.startswith('tiget.'):
        return True
    return False


def deep_reload(module):
    reloaded = set()

    def _reload(mod):
        reloaded.add(mod)
        if mod.__name__.startswith(module.__name__):
            for m in filter(ismodule, vars(mod).values()):
                if is_builtin(m.__name__) or m in reloaded:
                    continue
                elif m.__name__.startswith(module.__name__ + '.'):
                    _reload(m)
                elif not _is_in_tiget(m):
                    _reload(m)
        return reload(mod)
    return _reload(module)
