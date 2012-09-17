from collections import OrderedDict
from uuid import UUID, uuid4

from tiget.git import auto_transaction, get_transaction, GitError
from tiget.utils import serializer
from tiget.models.fields import Field, UUIDField


class DoesNotExist(Exception): pass
class MultipleObjectsReturned(Exception): pass
class InvalidObject(Exception): pass

MODEL_EXCEPTIONS = (DoesNotExist, MultipleObjectsReturned, InvalidObject)


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

        module = attrs['__module__']
        for exc_class in MODEL_EXCEPTIONS:
            exc = exc_class.__name__
            attrs[exc] = type(exc, (exc_class,), {'__module__': module})

        attrs['_storage_name'] = attrs.pop('storage_name', name.lower() + 's')

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
            raise self.invalid_field(k)

    def __repr__(self):
        hex_id = getattr(self.id, 'hex', None)
        return '{0}: {1}'.format(self.__class__.__name__, hex_id)

    def invalid_field(self, name):
        message = '\'{0}\' is an invalid field name for {1}'
        return TypeError(message.format(name, self.__class__.__name__))

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
            raise self.InvalidObject(str(e))
        for name, value in content.iteritems():
            try:
                field = self._fields[name]
            except KeyError:
                raise self.invalid_field(name)
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
        serialized = self.dumps(include_hidden=True)
        transaction.set_blob(self.path, serialized.encode('utf-8'))
        # TODO: create informative commit message
        transaction.add_message(
            u'Edit {0} {1}'.format(self.__class__.__name__, self.id.hex))

    @auto_transaction()
    def delete(self):
        raise NotImplementedError

    @classmethod
    @auto_transaction()
    def get_obj(cls, instance_id):
        if not isinstance(instance_id, UUID):
            instance_id = UUID(instance_id)
        transaction = get_transaction()
        instance = cls(id=instance_id)
        try:
            blob = transaction.get_blob(instance.path).decode('utf-8')
        except GitError:
            raise cls.DoesNotExist()
        instance.loads(blob)
        return instance

    @classmethod
    @auto_transaction()
    def all(cls):
        transaction = get_transaction()
        path = '/{0}'.format(cls._storage_name)
        instances = []
        for instance_id in transaction.list_blobs(path):
            instances += [cls.get_obj(instance_id)]
        return instances

    @classmethod
    def filter(cls, **kwargs):
        obj_id = kwargs.pop('id', None)
        if obj_id:
            try:
                objs = [cls.get_obj(obj_id)]
            except cls.DoesNotExist:
                objs = []
        else:
            objs = cls.all()
        filtered = []
        # TODO: use incidces for filtering
        for obj in objs:
            if all(obj._data[k] == v for k, v in kwargs.iteritems()):
                filtered += [obj]
        return filtered

    @classmethod
    def get(cls, **kwargs):
        objs = cls.filter(**kwargs)
        if len(objs) == 1:
            return objs[0]
        elif not objs:
            raise cls.DoesNotExist()
        else:
            raise cls.MultipleObjectsReturned()
