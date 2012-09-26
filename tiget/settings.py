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
    'branchname': StrSetting(default='tiget'),
    'debug': BoolSetting(default=False),
    'color': BoolSetting(default=True),
    'pdb_module': StrSetting(default='pdb'),
    'repository_path': StrSetting(default='.'),
}


class Settings(object):
    def __init__(self):
        self.data = {}

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key, value):
        if key == 'data':
            super(Settings, self).__setattr__(key, value)
        else:
            self[key] = value

    def __getitem__(self, key):
        setting = SETTINGS.get(key)
        if setting and not key in self.data:
            return setting.default
        return self.data[key]

    def __setitem__(self, key, value):
        setting = SETTINGS.get(key)
        if setting:
            setting.validate(value)
        self.data[key] = value

    def keys(self):
        keys = set(self.data.keys())
        keys.update(SETTINGS.keys())
        return list(keys)


settings = Settings()
