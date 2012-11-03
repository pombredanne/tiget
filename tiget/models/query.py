from tiget.git import auto_transaction, get_transaction, GitError


class Query(object):
    def __init__(self, model, **conditions):
        self.model = model
        if self.model._meta.pk.attname in conditions:
            conditions['pk'] = conditions.pop(self.model._meta.pk.attname)
        self.conditions = conditions

    def __or__(self, other):
        if not self.conditions:
            return self
        return OrQuery(self, other)

    def __and__(self, other):
        if not self.conditions:
            return other
        return AndQuery(self, other)

    def __invert__(self):
        return NotQuery(self)

    def __repr__(self):
        if not self.conditions:
            return '()'
        return ' AND '.join(
            '{}={!r}'.format(k, v) for k, v in self.conditions.items())

    @auto_transaction()
    def _fetch(self, pk, obj_cache):
        if not pk in obj_cache:
            obj = self.model(pk=pk)
            try:
                content = get_transaction().get_blob(obj.path).decode('utf-8')
            except GitError:
                raise self.model.DoesNotExist()
            obj.loads(content)
            obj_cache[pk] = obj
        return obj_cache[pk]

    def match(self, pk, obj_cache):
        if 'pk' in self.conditions and not pk == self.conditions['pk']:
            return False
        obj = self._fetch(pk, obj_cache)
        return all(getattr(obj, k) == v for k, v in self.conditions.items())

    def execute(self, obj_cache=None):
        # TODO: query optimization
        if obj_cache is None:
            obj_cache = {}
        with auto_transaction() as transaction:
            for pk in transaction.list_blobs([self.model._meta.storage_name]):
                pk = self.model._meta.pk.loads(pk)
                if self.match(pk, obj_cache):
                    yield pk


class NotQuery(Query):
    def __init__(self, subquery):
        self.subquery = subquery

    def match(self, *arg, **kwargs):
        return not self.subquery.match(*args, **kwargs)


class AndQuery(Query):
    def __init__(self, *subqueries):
        self.subqueries = subqueries

    def __and__(self, other):
        return AndQuery(other, *self.subqueries)

    def __repr__(self):
        return ' AND '.join('({!r})'.format(query) for query in self.subqueries)

    def match(self, *args, **kwargs):
        return all(query.match(*args, **kwargs) for query in self.subqueries)


class OrQuery(Query):
    def __init__(self, *subqueries):
        self.subqueries = subqueries

    def __or__(self, other):
        return OrQuery(other, *self.subqueries)

    def __repr__(self):
        return ' OR '.join('({!r})'.format(query) for query in self.subqueries)

    def match(self, *args, **kwargs):
        return any(query.match(*args, **kwargs) for query in self.subqueries)
