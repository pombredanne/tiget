import tiget

__author__ = tiget.__author__
__version__ = tiget.__version__


def load(plugin):
    from tiget.simple_workflow import models
    from tiget.simple_workflow.cmds import accept_cmd
    plugin.add_models(models)
    plugin.add_cmd(accept_cmd)
