from uuid import UUID

__all__ = ['UUIDField', 'TextField', 'ForeignKey']


class Field(object):
    field_type = None
    creation_counter = 0

    def __init__(self, default=None, hidden=False, null=False, primary_key=False):
        # TODO: implement unique constraints
        self._default = default
        self.hidden = hidden
        self.null = null
        self.primary_key = primary_key
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
            raise RuntimeError('{0} is not bound'.format(self.name))
        return self._name

    def bind(self, name):
        if self._name:
            raise RuntimeError('{0} is already bound'.format(self.name))
        self._name = name

    @property
    def default(self):
        default = self._default
        if hasattr(default, '__call__'):
            default = default()
        return default

    def clean(self, value):
        if not value is None and not isinstance(value, self.field_type):
            type_name = self.field_type.__name__
            raise ValueError(
                '{0} must be of type {1}'.format(self.name, type_name))
        if value is None and not self.null:
            raise ValueError('{0} must not be None'.format(self.name))
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
            return self.field_type.get(pk=s)
        return None
