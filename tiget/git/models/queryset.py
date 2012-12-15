from functools import reduce

from tiget.git import transaction
from tiget.git.models.query import Q


class ObjCache:
    def __init__(self, model):
        self.model = model
        self.cache = {}
        pks = transaction.current().list_blobs([model._meta.storage_name])
        self.pks = set(map(model._meta.pk.loads, pks))

    def __getitem__(self, pk):
        if not pk in self.cache:
            obj = self.model(pk=pk)
            try:
                content = transaction.current().get_blob(obj.path).decode('utf-8')
            except GitError:
                raise self.model.DoesNotExist('object does not exist')
            obj.loads(content)
            self.cache[pk] = obj
        return self.cache[pk]


class QuerySet:
    REPR_MAXLEN = 10

    def __init__(self, model, query=None):
        self.model = model
        if query is None:
            query = Q()
        self.query = query

    def __repr__(self):
        evaluated = list(self[:self.REPR_MAXLEN+1])
        if len(evaluated) > self.REPR_MAXLEN:
            bits = (repr(bit) for bit in evaluated[:self.REPR_MAXLEN-1])
            return '[{}, ...]'.format(', '.join(bits))
        return repr(evaluated)

    def __or__(self, other):
        return QuerySet(self.model, self.query | other.query)

    def __and__(self, other):
        return QuerySet(self.model, self.query & other.query)

    def __invert__(self):
        return QuerySet(self.model, ~self.query)

    @transaction.wrap()
    def __getitem__(self, key):
        if isinstance(key, slice):
            return QuerySet(self.model, self.query[key])
        elif isinstance(key, int):
            try:
                slice_ = slice(key, key+1)
                return QuerySet(self.model, self.query[slice_]).get()
            except self.model.DoesNotExist:
                raise IndexError('index out of range')
        else:
            raise TypeError('indices must be integers')

    @transaction.wrap()
    def __iter__(self):
        obj_cache = ObjCache(self.model)
        return iter([obj_cache[pk] for pk in self.execute(obj_cache)])

    @transaction.wrap()
    def execute(self, obj_cache=None):
        if obj_cache is None:
            obj_cache = ObjCache(self.model)
        return self.query.execute(obj_cache, pks=obj_cache.pks)

    def all(self):
        return self

    def filter(self, *args, **kwargs):
        query = reduce(lambda x, y: x & y, args, Q(**kwargs))
        return QuerySet(self.model, self.query & query)

    def exclude(self, *args, **kwargs):
        query = reduce(lambda x, y: x & y, args, Q(**kwargs))
        return QuerySet(self.model, self.query & ~query)

    def get(self):
        found = False
        for obj in self:
            if not found:
                found = True
            else:
                raise self.model.MultipleObjectsReturned(
                    'multiple objects returned')
        if not found:
            raise self.model.DoesNotExist('object does not exist')
        return obj

    def exists(self):
        return bool(self.execute())

    def count(self):
        return len(self.execute())

    def order_by(self, *order_by):
        # TODO: implement
        return self
