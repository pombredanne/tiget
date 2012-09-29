__author__ = 'Martin Natano <natano@natano.net>'
__version__ = '0.1a0'


def init_plugin(plugin):
    from tiget_ipython.cmds import ipython_cmd
    plugin.add_cmd(ipython_cmd)
