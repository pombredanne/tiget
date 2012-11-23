from uuid import uuid4

from tiget.git.models.fields import TextField


class Options(object):
    def __init__(self, meta):
        self.meta = meta
        self.fields = []
        self.pk = None
        self.storage_name = None

    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)
        self.model = cls
        self.storage_name = cls.__name__.lower() + 's'

        if self.meta:
            if hasattr(self.meta, 'storage_name'):
                self.storage_name = self.meta.storage_name

    def add_field(self, field):
        self.fields.append(field)
        if not self.pk and field.primary_key:
            self.pk = field

    def get_field(self, name):
        for f in self.fields:
            if f.name == name:
                return f
        raise KeyError(
            '{} has no field named {}'.format(self.model.__name__, name))

    def _prepare(self):
        if not self.pk:
            id_field = TextField(
                primary_key=True, hidden=True, default=lambda: uuid4().hex)
            self.model.add_to_class('id', id_field)
            self.fields.insert(0, self.fields.pop())
