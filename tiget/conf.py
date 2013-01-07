from tiget.plugins import plugins


class Settings:
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, key):
        return plugins[key].settings

    def keys(self):
        return plugins.keys()

    def parse_and_set(self, var):
        var, eq, value = var.partition('=')
        plugin, _, var = var.rpartition('.')
        if not plugin:
            plugin = 'core'
        if not eq:
            value = True
            if var.startswith('no'):
                var = var[2:]
                value = False
        try:
            self[plugin][var] = value
        except (ValueError, KeyError) as e:
            raise self.error(e)


settings = Settings()
