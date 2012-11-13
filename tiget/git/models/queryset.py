from tiget.git import transaction
from tiget.git.models.query import Query, ObjCache


class QuerySet(object):
    def __init__(self, model, query=None):
        self.model = model
        if query is None:
            query = Query()
        self.query = query

    def __or__(self, other):
        return QuerySet(self.model, self.query | other.query)

    def __and__(self, other):
        return QuerySet(self.model, self.query & other.query)

    def __not__(self):
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
        pks = self.query.execute(self.model, obj_cache)
        return iter([obj_cache[pk] for pk in pks])

    def filter(self, **conditions):
        query = self.query & Query(**conditions)
        return QuerySet(self.model, query)

    def exclude(self, **conditions):
        query = self.query & ~Query(**conditions)
        return QuerySet(self.model, query)

    def get(self):
        found = False
        for obj in self:
            if not found:
                found = True
            else:
                raise self.model.MultipleObjectsReturned()
        if not found:
            raise self.model.DoesNotExist()
        return obj

    @transaction.wrap()
    def exists(self):
        return any(True for _ in self.query.execute(self.model))

    @transaction.wrap()
    def count(self):
        return sum(1 for _ in self.query.execute(self.model))

    def order_by(self, *order_by):
        # TODO: implement
        return self
