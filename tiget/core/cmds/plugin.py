from tiget.cmds import cmd, CmdError
from tiget.plugins import load_plugin, unload_plugin, reload_plugin


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


@cmd()
def reload_cmd(opts, plugin_name):
    """
    reload plugin

    SYNOPSIS
        reload PLUGIN
    """
    try:
        reload_plugin(plugin_name)
    except KeyError:
        raise CmdError('no plugin "{}" loaded'.format(plugin_name))


@cmd()
def unload_cmd(opts, plugin_name):
    """
    unload plugin

    SYNOPSIS
        unload PLUGIN
    """
    try:
        unload_plugin(plugin_name)
    except KeyError:
        raise CmdError('no plugin "{}" loaded'.format(plugin_name))
