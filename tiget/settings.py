from tiget.plugins import plugins

__all__ = ['BoolSetting', 'StrSetting', 'settings']


class Setting(object):
    def __init__(self, default=None, choices=None):
        self.default = default
        self.choices = choices

    def validate(self, value):
        if not self.choices is None and not value in self.choices:
            raise ValueError('value must be in {}'.format(self.choices))


class BoolSetting(Setting):
    def validate(self, value):
        if not isinstance(value, bool):
            raise ValueError('value must be a boolean')
        super(BoolSetting, self).validate(value)


class StrSetting(Setting):
    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError('value must be a string')
        super(StrSetting, self).validate(value)


class Settings(object):
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
