from tiget.settings import StrSetting

__author__ = 'Martin Natano <natano@natano.net>'
__version__ = '0.1a0'


def init_plugin(plugin):
    from IPython.frontend.terminal import embed
    embed._embedded_shell = None

    from tiget_ipython.cmds import ipython_cmd
    plugin.add_cmd(ipython_cmd)
    plugin.add_setting('prompt', StrSetting(default='IPython[\\#]> '))
