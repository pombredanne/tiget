from tiget.git import auto_transaction
from tiget.models.query import Query


class QuerySet(object):
    def __init__(self, model, query=None):
        self.model = model
        if query is None:
            query = Query(model)
        self.query = query

    def __iter__(self):
        obj_cache = {}
        with auto_transaction():
            for pk in self.query.execute(obj_cache):
                yield self.query._fetch(pk, obj_cache)

    def __or__(self, other):
        return QuerySet(self.model, self.query | other.query)

    def __and__(self, other):
        return QuerySet(self.model, self.query & other.query)

    def __not__(self):
        return QuerySet(self.model, ~self.query)

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

    def exists(self):
        with auto_transaction():
            for pk in self.query.execute():
                return True
        return False

    def count(self):
        count = 0
        for pk in self.query.execute():
            count += 1
        return count

    def order_by(self, *order_by):
        # TODO: implement
        return self
