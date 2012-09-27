import pkg_resources


def load_plugin(plugin_name):
    found = False
    for ep in pkg_resources.iter_entry_points('tiget.plugins', plugin_name):
        found = True
        init_plugin = ep.load()
        init_plugin()
    if not found:
        raise KeyError(plugin_name)
