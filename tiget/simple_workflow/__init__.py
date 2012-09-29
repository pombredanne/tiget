import tiget

__author__ = tiget.__author__
__version__ = tiget.__version__


def init_plugin(plugin):
    from tiget.simple_workflow import models
    from tiget.simple_workflow.cmds import accept_cmd
    plugin.add_cmd(accept_cmd)
