import pkg_resources

from tiget.cmds import cmd, CmdError
from tiget.plugins import load_plugin, unload_plugin, reload_plugin, plugins


@cmd()
def load_cmd(opts, plugin_name=None):
    """
    load plugin

    SYNOPSIS
        load PLUGIN
    """
    if plugin_name:
        try:
            load_plugin(plugin_name)
        except ImportError as e :
            raise CmdError(e)
    else:
        print('Available plugins (plugins marked with * are loaded):')
        for ep in pkg_resources.iter_entry_points('tiget.plugins'):
            loaded = ep.name in plugins
            print('[{}] {}'.format('*' if loaded else ' ', ep.name))


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
