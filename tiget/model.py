from collections import OrderedDict
from uuid import UUID, uuid4
from tiget.git import auto_transaction, get_transaction
from tiget.utils import serializer

class Field(object):
    allowed_type = None
    creation_counter = 0

    def __init__(self, default=None, hidden=False, null=False):
        self._default = default
        self.hidden = hidden
        self.null = null
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
        if not value is None and not isinstance(value, self.allowed_type):
            raise ValueError('{0} must be of type {1}'.format(self.name, self.allowed_type.__name__))
        if value is None and not self.null:
            raise ValueError('{0} must not be None'.format(self.name))
        return value

    def dumps(self, value):
        if not value is None:
            value = unicode(value)
        return value

    def loads(self, s):
        if not s is None:
            return self.allowed_type(s)
        return None

class UUIDField(Field):
    allowed_type = UUID

    def dumps(self, value):
        if not value is None:
            return value.hex.decode('ascii')
        return None

class TextField(Field):
    allowed_type = unicode


class ObjectDoesNotExist(Exception): pass
class ValidationError(Exception): pass
class SerializationError(Exception): pass

class ModelBase(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        attrs['id'] = UUIDField(hidden=True, null=True)
        fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields += [(k, v)]
                v.bind(k)
        fields.sort(key=lambda x: x[1].creation_counter)
        fields = OrderedDict(fields)
        attrs['_fields'] = fields

        attrs['_storage_name'] = name.lower() + 's'

        module = attrs['__module__']
        attrs['DoesNotExist'] = type('DoesNotExist', (ObjectDoesNotExist,), {'__module__': module})
        attrs['ValidationError'] = type('ValidationError', (ValidationError,), {'__module__': module})
        attrs['SerializationError'] = type('SerializationError', (SerializationError,), {'__module__': module})

        return super_new(cls, name, bases, attrs)

class Model(object):
    __metaclass__ = ModelBase

    def __init__(self, **kwargs):
        self._data = {}
        for name, field in self._fields.iteritems():
            value = kwargs.pop(name, field.default)
            if not value is None:
                value = field.clean(value)
            self._data[name] = value
        for k in kwargs.iterkeys():
            raise TypeError('\'{0}\' is an invalid field name for {1}'.format(k, self.__class__.__name__))

    def __repr__(self):
        hex_id = getattr(self.id, 'hex', None)
        return '{0}: {1}'.format(self.__class__.__name__, hex_id)

    def update(self, **kwargs):
        for name, field in self._fields.iteritems():
            if name in kwargs:
                value = kwargs.pop(name)
                self._data[name] = value
            value = kwargs.pop(name, field.default)
            if not value is None:
                value = field.clean(value)
            self._data[name] = value
        for k in kwargs.iterkeys():
            raise TypeError('\'{0}\' is an invalid field name for {1}'.format(k, self.__class__.__name__))

    def dumps(self, include_hidden=False):
        content = OrderedDict()
        for name, field in self._fields.iteritems():
            if field.hidden and not include_hidden:
                continue
            value = self._data[name]
            content[name] = field.dumps(value)
        return serializer.dumps(content)

    def loads(self, s):
        try:
            content = serializer.loads(s)
        except ValueError as e:
            raise self.SerializationError()
        for name, value in content.iteritems():
            # FIXME: raise error if field does not exist
            field = self._fields[name]
            self._data[name] = field.loads(value)

    @property
    def path(self):
        return '/{0}/{1}'.format(self._storage_name, self.id.hex)

    @auto_transaction()
    def save(self):
        for name, field in self._fields.iteritems():
            field.clean(self._data[name])
        if not self.id:
            self.id = uuid4()
        transaction = get_transaction()
        transaction[self.path] = self.dumps(include_hidden=True)
        # TODO: create informative commit message
        transaction.add_message(u'Edit ticket {0}'.format(self.id.hex))

    @auto_transaction()
    def delete(self):
        raise NotImplementedError

    @classmethod
    @auto_transaction()
    def get(cls, instance_id):
        if not isinstance(instance_id, UUID):
            instance_id = UUID(instance_id)
        transaction = get_transaction()
        instance = cls(id=instance_id)
        try:
            blob = transaction[instance.path]
        except GitError:
            raise self.DoesNotExist()
        instance.loads(blob)
        return instance

    @classmethod
    @auto_transaction()
    def all(cls):
        transaction = get_transaction()
        path = '/{0}'.format(cls._storage_name)
        instances = []
        for instance_id in transaction.list_blobs(path):
            instances += [cls.get(instance_id)]
        return instances
