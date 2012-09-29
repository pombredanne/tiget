from tiget.cmds import cmd, CmdError
from tiget.plugins import load_plugin


@cmd()
def load_cmd(opts, plugin_name):
    """
    load plugin

    SYNOPSIS
        load PLUGIN
    """
    try:
        load_plugin(plugin_name)
    except ImportError as e :
        raise CmdError(e)
