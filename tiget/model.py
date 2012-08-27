from collections import OrderedDict
from uuid import UUID, uuid4
from tiget.git import auto_transaction, get_transaction
from tiget.utils import serializer

class Field(object):
    creation_counter = 0

    def __init__(self, default=None, hidden=False):
        self._default = default
        self.hidden = hidden
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    @property
    def default(self):
        default = self._default
        if hasattr(default, '__call__'):
            default = default()
        return default

    def clean(self, value):
        return value

    def dumps(self, value):
        return value

    def loads(self, s):
        return s

class FieldProxy(object):
    def __init__(self, name, field):
        self.name = name
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance._data.get(self.name, self.field.default)

    def __set__(self, instance, value):
        if value is None:
            del instance._data[self.name]
            return
        instance._data[self.name] = self.field.clean(value)

class UUIDField(Field):
    def clean(self, value):
        if not isinstance(value, UUID):
            raise ValueError('not a UUID')
        return value

    def dumps(self, value):
        return value.hex.decode('ascii')

    def loads(self, s):
        return UUID(s)

class TextField(Field):
    def clean(self, value):
        if not isinstance(value, unicode):
            raise ValueError('not a unicode string')
        return value

class ModelBase(type):
    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if parents:
            attrs['id'] = UUIDField(hidden=True)
            fields = []
            for k, v in attrs.items():
                if isinstance(v, Field):
                    fields += [(k, v)]
                    attrs[k] = FieldProxy(k, v)
            fields.sort(key=lambda x: x[1].creation_counter)
            fields = OrderedDict(fields)
            attrs['_fields'] = fields
        return super(ModelBase, cls).__new__(cls, name, bases, attrs)

class Model(object):
    __metaclass__ = ModelBase

    class ValidationError(Exception): pass

    def __init__(self, **kwargs):
        self._data = {}
        for name, field in self._fields.iteritems():
            value = kwargs.pop(name, None)
            if not value is None:
                self._data[name] = field.clean(value)
        # TODO: raise exception on invalid kwargs

    def __repr__(self):
        hex_id = getattr(self.id, 'hex', None)
        return '{0}: {1}'.format(self.__class__.__name__, hex_id)

    def dumps(self, include_hidden=False):
        content = OrderedDict()
        for name, field in self._fields.iteritems():
            if field.hidden and not include_hidden:
                continue
            value = self._data.get(name, field.default)
            content[name] = field.dumps(value)
        return serializer.dumps(content)

    def loads(self, s):
        content = serializer.loads(s)
        for name, field in self._fields.iteritems():
            if name in content:
                value = content.pop(name)
                self._data[name] = field.loads(value)
        # TODO: raise exception on invalid content

    @classmethod
    def get_storage_name(cls):
        return cls.__name__.lower() + 's'

    @auto_transaction()
    def save(self):
        if not self.id:
            self.id = uuid4()
        transaction = get_transaction()
        path = '/{0}/{1}'.format(self.get_storage_name(), self.id.hex)
        transaction[path] = self.dumps(include_hidden=True)
        # TODO: better commit message
        transaction.add_message(u'Edit ticket {0}'.format(self.id.hex))

    @classmethod
    @auto_transaction()
    def get(cls, instance_id):
        if isinstance(instance_id, UUID):
            instance_id = instance_id.hex
        transaction = get_transaction()
        path = '/{0}/{1}'.format(cls.get_storage_name(), instance_id)
        instance = cls()
        instance.loads(transaction.get_blob(path))
        return instance

    @classmethod
    @auto_transaction()
    def all(cls):
        transaction = get_transaction()
        path = '/{0}'.format(cls.get_storage_name())
        instances = []
        for instance_id in transaction.list_blobs(path):
            instances += [cls.get(instance_id)]
        return instances
