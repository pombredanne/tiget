from collections import OrderedDict
from uuid import UUID, uuid4

from tiget.git import auto_transaction, get_transaction, GitError
from tiget.utils import quote_filename, unquote_filename
from tiget.serializer import dumps, loads
from tiget.models.fields import Field, UUIDField


class DoesNotExist(Exception): pass
class MultipleObjectsReturned(Exception): pass
class InvalidObject(Exception): pass

MODEL_EXCEPTIONS = (DoesNotExist, MultipleObjectsReturned, InvalidObject)


class ModelBase(type):
    @classmethod
    def __prepare__(cls, name, bases):
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if parents:
            return OrderedDict()
        return super(ModelBase, cls).__prepare__(name, bases)

    def __new__(cls, cls_name, bases, attrs):
        super_new = super(ModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, cls_name, bases, attrs)

        pk_field = None
        fields = OrderedDict()
        for key, value in attrs.items():
            if not isinstance(value, Field):
                continue
            fields[key] = value
            if value.primary_key and pk_field is None:
                pk_field = value
            elif value.primary_key:
                raise RuntimeError('more than one primary key specified')

        if pk_field is None:
            id_field = UUIDField(
                hidden=True, primary_key=True, default=lambda: uuid4())
            attrs['id'] = id_field
            fields['id'] = id_field
            fields.move_to_end('id', last=False)
            pk_field = id_field

        for name, field in fields.items():
            field.bind(name)

        attrs['_primary_key'] = pk_field.name
        attrs['_fields'] = fields
        attrs['_storage_name'] = cls_name.lower() + 's'
        module = attrs['__module__']
        for exc_class in MODEL_EXCEPTIONS:
            name = exc_class.__name__
            attrs[name] = type(name, (exc_class,), {'__module__': module})
        return super_new(cls, cls_name, bases, attrs)


class Model(object, metaclass=ModelBase):
    def __init__(self, **kwargs):
        self._data = {name: f.default for name, f in self._fields.items()}
        for key, value in self.normalize_kwargs(**kwargs).items():
            self._data[key] = self._fields[key].clean(value)

    @classmethod
    def normalize_kwargs(cls, **kwargs):
        if 'pk' in kwargs:
            kwargs[cls._primary_key] = kwargs.pop('pk')
        for key in kwargs.keys():
            if not key in cls._fields:
                raise KeyError(
                    '{} has no field "{}"'.format(self.__class__.__name__, key))
        return kwargs

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.pk)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.pk)

    def dumps(self, include_hidden=False):
        content = OrderedDict()
        for name, field in self._fields.items():
            if field.hidden and not include_hidden:
                continue
            value = self._data[name]
            content[name] = field.dumps(value)
        return dumps(content)

    def loads(self, s):
        try:
            content = loads(s)
            for key, value in self.normalize_kwargs(**content).items():
                self._data[key] = self._fields[key].loads(value)
        except (ValueError, KeyError) as e:
            raise self.InvalidObject(e)

    @property
    def path(self):
        pk = self.pk
        if pk is None:
            raise ValueError('pk must not be None')
        pk = self._fields[self._primary_key].dumps(pk)
        return '/{}/{}'.format(self._storage_name, quote_filename(pk))

    @auto_transaction()
    def save(self):
        for name, field in self._fields.items():
            try:
                field.clean(self._data[name])
            except ValueError as e:
                raise self.InvalidObject(e)
        transaction = get_transaction()
        serialized = self.dumps(include_hidden=True)
        transaction.set_blob(self.path, serialized.encode('utf-8'))
        # TODO: create informative commit message
        transaction.add_message('Edit {}'.format(self))

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
            content = transaction.get_blob(instance.path).decode('utf-8')
        except GitError:
            raise cls.DoesNotExist('{} does not exist'.format(cls.__name__))
        instance.loads(content)
        return instance

    @classmethod
    @auto_transaction()
    def all(cls):
        transaction = get_transaction()
        path = '/{}'.format(cls._storage_name)
        instances = []
        for pk in transaction.list_blobs(path):
            instances += [cls.get_obj(unquote_filename(pk))]
        return instances

    @classmethod
    def filter(cls, **kwargs):
        if 'pk' in kwargs:
            kwargs[cls._primary_key] = kwargs.pop('pk')
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
            if all(obj._data[k] == v for k, v in kwargs.items()):
                filtered += [obj]
        return filtered

    @classmethod
    def get(cls, **kwargs):
        objs = cls.filter(**kwargs)
        if len(objs) == 1:
            return objs[0]
        elif not objs:
            raise cls.DoesNotExist('{} does not exist'.format(cls.__name__))
        else:
            raise cls.MultipleObjectsReturned()

    @property
    def pk(self):
        return getattr(self, self._primary_key)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.pk == other.pk
        return False

    def __ne__(self, other):
        return not self == other
