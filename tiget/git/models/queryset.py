from tiget.git import transaction
from tiget.git.models.query import Query, ObjCache


class QuerySet(object):
    def __init__(self, model, query=None):
        self.model = model
        if query is None:
            query = Query(model)
        self.query = query

    def __or__(self, other):
        return QuerySet(self.model, self.query | other.query)

    def __and__(self, other):
        return QuerySet(self.model, self.query & other.query)

    def __not__(self):
        return QuerySet(self.model, ~self.query)

    @transaction.wrap()
    def __bool__(self):
        return any(True for _ in self.query.execute(self.model))

    @transaction.wrap()
    def __len__(self):
        return sum(1 for _ in self.query.execute(self.model))

    @transaction.wrap()
    def __iter__(self):
        obj_cache = ObjCache(self.model)
        pks = self.query.execute(self.model, obj_cache)
        return iter([obj_cache[pk] for pk in pks])

    def filter(self, **conditions):
        query = self.query & Query(self.model, **conditions)
        return QuerySet(self.model, query)

    def exclude(self, **conditions):
        query = self.query & ~Query(self.model, **conditions)
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

    def order_by(self, *order_by):
        # TODO: implement
        return self
