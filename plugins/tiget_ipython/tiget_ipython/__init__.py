from IPython.frontend.terminal import embed

from tiget.plugins.api import *
from tiget_ipython.cmds import IPythonCmd


def load(plugin):
    plugin.add_cmd(IPythonCmd)
    plugin.add_setting('prompt', StrSetting(default='IPython[\\#]> '))


def unload(plugin):
    embed._embedded_shell = None
