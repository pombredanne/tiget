import tiget

__author__ = tiget.__author__
__version__ = tiget.__version__


def load(plugin):
    from tiget.scrum import models
    from tiget.scrum.cmds import accept_cmd
    plugin.add_models(models)
    plugin.add_cmd(accept_cmd)
