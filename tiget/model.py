from collections import OrderedDict
from uuid import uuid4
from tiget.git import auto_transaction, get_transaction
from tiget.utils import serialize, deserialize

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

class TextField(Field):
    pass

class ModelBase(type):
    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if parents:
            fields = []
            for k, v in attrs.items():
                if isinstance(v, Field):
                    fields += [(k, v)]
                    del attrs[k]
            fields.sort(key=lambda x: x[1].creation_counter)
            fields = OrderedDict(fields)
            if not 'id' in fields:
                fields['id'] = TextField(default=lambda: uuid4().hex, hidden=True)
            attrs['fields'] = fields
        return super(ModelBase, cls).__new__(cls, name, bases, attrs)

class Model(object):
    __metaclass__ = ModelBase

    def __init__(self, **kwargs):
        self.data = {}
        for k, v in kwargs.iteritems():
            if not k in self.fields.keys():
                raise Exception('field "{0}" does not exist'.format(k))
            self.data[k] = v
            transaction.add_message(u'Initialize Repository')

    def __getattr__(self, name):
        field = self.fields.get(name, None)
        if field:
            return self.data.get(name, field.default)
        raise AttributeError

    def __setattr__(self, name, value):
        if name in self.fields:
            self.data[name] = value
        else:
            super(Model, self).__setattr__(name, value)

    def serialize(self, include_hidden=False):
        content = OrderedDict()
        for name, field in self.fields.iteritems():
            if not include_hidden and field.hidden:
                continue
            value = self.data.get(name, field.default)
            content[name] = value
        return serialize(content)

    def deserialize(self, s):
        content = deserialize(s)
        for k, v in content.iteritems():
            self.data[name] = value

    @classmethod
    def get_storage_name(cls):
        return cls.__name__.lower() + 's'

    @auto_transaction()
    def save(self):
        transaction = get_transaction()
        path = '/{0}/{1}'.format(self.get_storage_name(), self.id)
        transaction[path] = self.serialize(include_hidden=True)
        # TODO: better commit message
        transaction.add_message(u'Edit ticket {0}'.format(self.id))

    @classmethod
    def get(cls, instance_id):
        raise NotImplementedError

    @classmethod
    def all(cls):
        transaction = get_transaction()
        path = '/{0}'.format(cls.get_storage_name())
        instances = []
        for name in transaction.list_blobs(path):
            instance = cls()
            path = '/{0}/{1}'.format(cls.get_storage_name(), name)
            instance.deserialize(transaction.get_blob(path))
            instances += [instance]
        return instances
