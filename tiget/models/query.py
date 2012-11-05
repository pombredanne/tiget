from tiget.git import get_transaction, GitError


class ObjCache(object):
    def __init__(self, model):
        self.model = model
        self.cache = {}

    def __getitem__(self, pk):
        if not pk in self.cache:
            obj = self.model(pk=pk)
            try:
                content = get_transaction().get_blob(obj.path).decode('utf-8')
            except GitError:
                raise self.model.DoesNotExist()
            obj.loads(content)
            self.cache[pk] = obj
        return self.cache[pk]


class Query(object):
    def __init__(self, model, **conditions):
        self.conditions = conditions

    def __or__(self, other):
        return OrQuery(self, other)

    def __and__(self, other):
        return AndQuery(self, other)

    def __invert__(self):
        return NotQuery(self)

    def __repr__(self):
        conditions = ' AND '.join(
            '{}={!r}'.format(k, v) for k, v in self.conditions.items())
        return '({})'.format(conditions)

    def match(self, model, pk, obj_cache):
        for key in ('pk', model._meta.pk.attname):
            if key in self.conditions and not pk == self.conditions[key]:
                return False
        obj = obj_cache[pk]
        return all(getattr(obj, k) == v for k, v in self.conditions.items())

    def execute(self, model, obj_cache=None):
        # TODO: query optimization
        if obj_cache is None:
            obj_cache = ObjCache(model)
        transaction = get_transaction()
        for pk in transaction.list_blobs([model._meta.storage_name]):
            pk = model._meta.pk.loads(pk)
            if self.match(model, pk, obj_cache):
                yield pk


class NotQuery(Query):
    def __init__(self, subquery):
        self.subquery = subquery

    def __repr__(self):
        return '(NOT {!r})'.format(self.subquery)

    def match(self, *arg, **kwargs):
        return not self.subquery.match(*args, **kwargs)


class AndQuery(Query):
    def __init__(self, *subqueries):
        self.subqueries = subqueries

    def __and__(self, other):
        return AndQuery(other, *self.subqueries)

    def __repr__(self):
        r = ' AND '.join('{!r}'.format(query) for query in self.subqueries)
        return '({})'.format(r)

    def match(self, *args, **kwargs):
        return all(query.match(*args, **kwargs) for query in self.subqueries)


class OrQuery(Query):
    def __init__(self, *subqueries):
        self.subqueries = subqueries

    def __or__(self, other):
        return OrQuery(other, *self.subqueries)

    def __repr__(self):
        r =' OR '.join('{!r}'.format(query) for query in self.subqueries)
        return '({})'.format(r)

    def match(self, *args, **kwargs):
        return any(query.match(*args, **kwargs) for query in self.subqueries)