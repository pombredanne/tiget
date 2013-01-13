__all__ = ['Setting', 'BoolSetting', 'IntSetting', 'StrSetting']


class Setting:
    def __init__(self, default=None, choices=None):
        self.default = default
        self.choices = choices

    def clean(self, value):
        if not self.choices is None and not value in self.choices:
            raise ValueError('value must be in {}'.format(self.choices))
        return value

    def changed(self, value):
        pass

    def format(self, value):
        if value is None:
            return '<null>'
        return str(value)


class BoolSetting(Setting):
    def clean(self, value):
        if value == 'on':
            value = True
        elif value == 'off':
            value = False
        elif not isinstance(value, bool):
            raise ValueError('value must be a boolean')
        return super().clean(value)

    def format(self, value):
        if value is True:
            return 'on'
        elif value is False:
            return 'off'
        else:
            return super().format(value)


class IntSetting(Setting):
    def clean(self, value):
        if not value is None and not isinstance(value, int):
            value = int(value)
        return super().clean(value)


class StrSetting(Setting):
    def clean(self, value):
        if not value is None and not isinstance(value, str):
            raise ValueError('value must be a string')
        return super().clean(value)


class Settings:
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
        return self.data.get(key, variable.default)

    def __setitem__(self, key, value):
        try:
            variable = self.variables[key]
        except KeyError:
            raise KeyError('invalid setting "{}"'.format(key))
        self.data[key] = variable.clean(value)
        variable.changed(self.data[key])

    def __len__(self):
        return len(self.variables)

    def __contains__(self, key):
        return key in self.variables

    def keys(self):
        return self.variables.keys()

    def get_display(self, key):
        try:
            variable = self.variables[key]
        except KeyError:
            raise KeyError('invalid setting "{}"'.format(key))
        value = self.data.get(key, variable.default)
        return variable.format(value)
