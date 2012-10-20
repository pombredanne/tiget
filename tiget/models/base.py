from collections import OrderedDict

from tiget import serializer
from tiget.git import auto_transaction, get_transaction, GitError
from tiget.utils import quote_filename, unquote_filename
from tiget.models.options import Options


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
        return super().__prepare__(name, bases)

    def __new__(cls, cls_name, bases, attrs):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, cls_name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, cls_name, bases, {'__module__': module})

        opts = Options(attrs.pop('Meta', None))
        new_class.add_to_class('_meta', opts)

        for exc_class in MODEL_EXCEPTIONS:
            name = exc_class.__name__
            exc_class = type(name, (exc_class,), {'__module__': module})
            new_class.add_to_class(name, exc_class)

        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        opts._prepare()
        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Model(object, metaclass=ModelBase):
    def __init__(self, **kwargs):
        self._data = {}
        for field in self._meta.fields:
            try:
                val = kwargs.pop(field.attname)
            except KeyError:
                val = field.get_default()
            setattr(self, field.attname, val)
        if kwargs:
            for prop in list(kwargs.keys()):
                try:
                    if isinstance(getattr(self.__class__, prop), property):
                        setattr(self, prop, kwargs.pop(prop))
                except AttributeError:
                    pass
            if kwargs:
                raise TypeError(
                    'invalid keyword argument \'{}\''.format(kwargs[0]))

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.pk)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.pk)

    def _get_pk_val(self):
        return getattr(self, self._meta.pk.attname)

    def _set_pk_val(self, value):
        return setattr(self, self._meta.pk.attname, value)

    pk = property(_get_pk_val, _set_pk_val)

    def dumps(self, include_hidden=False):
        data = OrderedDict()
        for field in self._meta.fields:
            if field.hidden and not include_hidden:
                continue
            value = getattr(self, field.attname)
            data[field.name] = field.dumps(value)
        return serializer.dumps(data)

    def loads(self, s):
        try:
            data = serializer.loads(s)
            for field_name, value in data.items():
                field = self._meta.get_field(field_name)
                setattr(self, field.attname, field.loads(value))
        except (ValueError, KeyError) as e:
            raise self.InvalidObject(e)

    @property
    def path(self):
        pk = self.pk
        if pk is None:
            raise ValueError('pk must not be None')
        pk = self._meta.pk.dumps(self.pk)
        return '/{}/{}'.format(self._meta.storage_name, quote_filename(pk))

    @auto_transaction()
    def save(self):
        for field in self._meta.fields:
            try:
                field.clean(getattr(self, field.attname))
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
        pk = cls._meta.pk.loads(pk)
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
        path = '/{}'.format(cls._meta.storage_name)
        instances = []
        for pk in transaction.list_blobs(path):
            instances += [cls.get_obj(unquote_filename(pk))]
        return instances

    @classmethod
    def filter(cls, **kwargs):
        if 'pk' in kwargs:
            kwargs[cls._meta.pk.attname] = kwargs.pop('pk')
        pk = kwargs.pop(cls._meta.pk.attname, None)
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

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.pk == other.pk

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.pk)
