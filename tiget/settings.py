from UserDict import UserDict


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
        if not isinstance(value, basestring):
            raise ValueError('value must be a string')
        super(StrSetting, self).validate(value)


SETTINGS = {
    'color': BoolSetting(default=True),
    'branchname': StrSetting(default='tiget'),
    'repository_path': StrSetting(default='.'),
}


class Settings(UserDict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, key):
        setting = SETTINGS.get(key)
        if setting and not key in self:
            return setting.default
        return UserDict.__getitem__(self, key)

    def __setitem__(self, key, value):
        setting = SETTINGS.get(key)
        if setting:
            setting.validate(value)
        UserDict.__setitem__(self, key, value)

    def keys(self):
        keys = set(UserDict.keys(self))
        keys.update(SETTINGS.keys())
        return list(keys)


settings = Settings()
