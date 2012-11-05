from tiget.git import transaction
from tiget.models.query import Query, ObjCache


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

    def __iter__(self):
        obj_cache = ObjCache(self.model)
        for pk in self.query.execute(self.model, obj_cache):
            yield obj_cache[pk]

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

    @transaction.wrap()
    def exists(self):
        return any(True for _ in self.query.execute(self.model))

    @transaction.wrap()
    def count(self):
        return sum(1 for _ in self.query.execute(self.model))

    def order_by(self, *order_by):
        # TODO: implement
        return self
