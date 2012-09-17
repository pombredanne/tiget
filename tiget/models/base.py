from collections import OrderedDict
from uuid import UUID, uuid4

from tiget.git import auto_transaction, get_transaction, GitError
from tiget.utils import serializer, quote_filename, unquote_filename
from tiget.models.fields import Field, UUIDField


class DoesNotExist(Exception): pass
class MultipleObjectsReturned(Exception): pass
class InvalidObject(Exception): pass

MODEL_EXCEPTIONS = (DoesNotExist, MultipleObjectsReturned, InvalidObject)


class ModelBase(type):
    def __new__(cls, cls_name, bases, attrs):
        super_new = super(ModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, cls_name, bases, attrs)

        fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields += [(k, v)]
        fields.sort(key=lambda x: x[1].creation_counter)
        fields = OrderedDict(fields)

        pk_fields = [f for f in fields.itervalues() if f.primary_key]
        if len(pk_fields) > 1:
            raise RuntimeError('more than one primary key specified')
        elif not pk_fields:
            id_field = UUIDField(
                hidden=True, primary_key=True, default=lambda: uuid4())
            attrs['id'] = id_field
            fields['id'] = id_field
            pk_fields = [id_field]

        for name, field in fields.iteritems():
            field.bind(name)

        attrs['_primary_key'] = pk_fields[0].name
        attrs['_fields'] = fields
        attrs['_storage_name'] = cls_name.lower() + 's'
        module = attrs['__module__']
        for exc_class in MODEL_EXCEPTIONS:
            name = exc_class.__name__
            attrs[name] = type(name, (exc_class,), {'__module__': module})
        return super_new(cls, cls_name, bases, attrs)


class Model(object):
    __metaclass__ = ModelBase

    def __init__(self, **kwargs):
        pk = kwargs.pop('pk', None)
        if not pk is None:
            kwargs[self._primary_key] = pk
        self._data = {}
        for name, field in self._fields.iteritems():
            value = kwargs.pop(name, field.default)
            if not value is None:
                value = field.clean(value)
            self._data[name] = value
        for k in kwargs.iterkeys():
            raise self.invalid_field(k)

    def __repr__(self):
        pk = self._data[self._primary_key]
        return '{0}: {1}'.format(self.__class__.__name__, pk)

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
        pk = self._data[self._primary_key]
        if pk is None:
            raise ValueError('pk must not be None')
        pk = self._fields[self._primary_key].dumps(pk)
        return '/{0}/{1}'.format(self._storage_name, quote_filename(pk))

    @auto_transaction()
    def save(self):
        for name, field in self._fields.iteritems():
            field.clean(self._data[name])
        transaction = get_transaction()
        serialized = self.dumps(include_hidden=True)
        transaction.set_blob(self.path, serialized.encode('utf-8'))
        # TODO: create informative commit message
        transaction.add_message(u'Edit {}'.format(self))

    @auto_transaction()
    def delete(self):
        raise NotImplementedError

    @classmethod
    @auto_transaction()
    def get_obj(cls, pk):
        pk = cls._fields[cls._primary_key].loads(pk)
        transaction = get_transaction()
        instance = cls(pk=pk)
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
        for pk in transaction.list_blobs(path):
            instances += [cls.get_obj(unquote_filename(pk))]
        return instances

    @classmethod
    def filter(cls, **kwargs):
        pk = kwargs.pop('pk', None)
        if not pk is None:
            kwargs[cls._primary_key] = pk
        pk = kwargs.pop(cls._primary_key, None)
        if not pk is None:
            try:
                objs = [cls.get_obj(pk)]
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
