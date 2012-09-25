from uuid import UUID

__all__ = ['UUIDField', 'TextField', 'ForeignKey']


class Field(object):
    field_type = None
    creation_counter = 0

    def __init__(
            self, hidden=False, null=False, primary_key=False, choices=None,
            default=None):
        self.hidden = hidden
        self.null = null
        self.primary_key = primary_key
        self.choices = choices
        self._default = default
        self._name = None
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance._data[self.name]

    def __set__(self, instance, value):
        instance._data[self.name] = self.clean(value)

    @property
    def name(self):
        if not self._name:
            raise RuntimeError('{} is not bound'.format(self.name))
        return self._name

    def bind(self, name):
        if self._name:
            raise RuntimeError('{} is already bound'.format(self.name))
        self._name = name

    @property
    def default(self):
        default = self._default
        if hasattr(default, '__call__'):
            default = default()
        return default

    def clean(self, value):
        if value is None:
            if not self.null:
                raise ValueError('{} must not be None'.format(self.name))
        else:
            if not isinstance(value, self.field_type):
                type_name = self.field_type.__name__
                raise ValueError(
                    '{} must be of type {}'.format(self.name, type_name))
            elif not self.choices is None and not value in self.choices:
                raise ValueError(
                    '{} must be in {}'.format(self.name, self.choices))
        return value

    def dumps(self, value):
        if not value is None:
            value = unicode(value)
        return value

    def loads(self, s):
        if not s is None:
            return self.field_type(s)
        return None


class UUIDField(Field):
    field_type = UUID

    def dumps(self, value):
        if not value is None:
            return value.hex.decode('ascii')
        return None


class TextField(Field):
    field_type = unicode


class ForeignKey(Field):
    def __init__(self, foreign_model, **kwargs):
        super(ForeignKey, self).__init__(**kwargs)
        self.field_type = foreign_model

    def dumps(self, value):
        if not value is None:
            pk_field = value._fields[value._primary_key]
            return pk_field.dumps(value._data[value._primary_key])
        return None

    def loads(self, s):
        if not s is None:
            try:
                return self.field_type.get(pk=s)
            except self.field_type.DoesNotExist as e:
                raise ValueError('{} does not exist'.format(self.name))
        return None
