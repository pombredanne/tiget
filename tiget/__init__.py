from tiget.plugins import load_plugin

from tiget.version import VERSION as __version__
__author__ = 'Martin Natano <natano@natano.net>'


BUILTIN_PLUGINS = ('core', 'importer', 'scrum')

for plugin_name in BUILTIN_PLUGINS:
    load_plugin(plugin_name)
