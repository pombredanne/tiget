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
        super().validate(value)


class StrSetting(Setting):
    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError('value must be a string')
        super().validate(value)


class Settings(object):
    def __init__(self):
        self.variables = {}
        self.data = {}

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key, value):
        if key in ('variables', 'data') or not key in self:
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __getitem__(self, key):
        try:
            variable = self.variables[key]
        except KeyError:
            raise KeyError('invalid setting "{}"'.format(key))
        if not key in self.data:
            return variable.default
        return self.data[key]

    def __setitem__(self, key, value):
        try:
            variable = self.variables[key]
        except KeyError:
            raise KeyError('invalid setting "{}"'.format(key))
        variable.validate(value)
        self.data[key] = value

    def __len__(self):
        return len(self.variables)

    def __contains__(self, key):
        return key in self.variables

    def keys(self):
        return self.variables.keys()
