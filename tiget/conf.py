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


settings = Settings()
