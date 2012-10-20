from uuid import UUID

__all__ = ['UUIDField', 'TextField', 'ForeignKey']


class Field(object):
    field_type = None

    def __init__(
            self, hidden=False, null=False, primary_key=False, choices=None,
            default=None, name=None):
        self.hidden = hidden
        self.null = null
        self.primary_key = primary_key
        self.choices = choices
        self.default = default
        self.name = name

    def contribute_to_class(self, cls, name):
        if not self.name:
            self.name = name
        self.attname = self.get_attname()
        self.model = cls
        cls._meta.add_field(self)

    def get_attname(self):
        return self.name

    def get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

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
            value = str(value)
        return value

    def loads(self, s):
        if not s is None:
            return self.field_type(s)
        return None


class UUIDField(Field):
    field_type = UUID

    def dumps(self, value):
        if not value is None:
            return value.hex
        return None


class TextField(Field):
    field_type = str


class ForeignKey(Field):
    def __init__(self, foreign_model, **kwargs):
        super(ForeignKey, self).__init__(**kwargs)
        self.field_type = foreign_model

    def dumps(self, value):
        if not value is None:
            pk_field = value._meta.pk
            return pk_field.dumps(value.pk)
        return None

    def loads(self, s):
        if not s is None:
            try:
                return self.field_type.get(pk=s)
            except self.field_type.DoesNotExist as e:
                raise ValueError('{} does not exist'.format(self.name))
        return None
