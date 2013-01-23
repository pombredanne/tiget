from tiget.plugins import load_plugin


BUILTIN_PLUGINS = ('core', 'importer', 'scrum')

for plugin_name in BUILTIN_PLUGINS:
    load_plugin(plugin_name)
