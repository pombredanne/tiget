import pkg_resources


def load_plugin(plugin_name):
    if ':' in plugin_name:
        try:
            module_path, attrs = plugin_name.split(':', 1)
        except ValueError:
            raise ImportError('malformed entry point "{}"'.format(entry_point))
        entry = __import__(module_path, fromlist=['__name__'])
        for attr in attrs.split('.'):
            try:
                entry = getattr(entry, attr)
            except AttributeError:
                raise ImportError(
                    '{} has no attribute "{}"'.format(entry, attr))
        init_plugin = entry
    else:
        for ep in pkg_resources.iter_entry_points('tiget.plugins', plugin_name):
            init_plugin = ep.load()
            break
        else:
            raise ImportError('plugin "{}" does not exist'.format(plugin_name))
    init_plugin()
