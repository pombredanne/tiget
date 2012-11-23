import re
from itertools import islice

from tiget.git import transaction, GitError


class ObjCache(object):
    def __init__(self, model):
        self.model = model
        self.cache = {}

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


class Query(object):
    def __or__(self, other):
        for a, b in ((self, other), (other, self)):
            if isinstance(a, Q) and not a.conditions:
                return a
            elif (isinstance(a, InvertedQ) and isinstance(a.subquery, Q)
                    and not a.subquery.conditions):
                return b
            elif isinstance(a, UnionQ) and isinstance(b, UnionQ):
                return UnionQ(*(a.subqueries + b.subqueries))
            elif (isinstance(a, InvertedQ) and isinstance(b, Q)
                    and isinstance(a.subquery, Q)
                    and a.subquery.conditions == b.conditions):
                return Q()
        return UnionQ(self, other)

    def __and__(self, other):
        for a, b in ((self, other), (other, self)):
            if isinstance(a, Q) and not a.conditions:
                return b
            elif (isinstance(a, InvertedQ) and isinstance(a.subquery, Q)
                    and not a.subquery.conditions):
                return a
            elif isinstance(a, IntersectionQ) and isinstance(b, IntersectionQ):
                return IntersectionQ(*(a.subqueries + b.subqueries))
            elif (isinstance(a, InvertedQ) and isinstance(b, Q)
                    and isinstance(a.subquery, Q)
                    and a.subquery.conditions == b.conditions):
                return ~Q()
        return IntersectionQ(self, other)

    def __invert__(self):
        return InvertedQ(self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return SliceQ(self, key)
        raise TypeError('index must be a slice')

    def match(self, model, pk, obj_cache):
        raise NotImplementedError

    def execute(self, model, obj_cache=None):
        # TODO: query optimization
        if obj_cache is None:
            obj_cache = ObjCache(model)
        trans = transaction.current()
        for pk in trans.list_blobs([model._meta.storage_name]):
            pk = model._meta.pk.loads(pk)
            if self.match(model, pk, obj_cache):
                yield pk


class Q(Query):
    OPERATORS = {
        'exact': lambda x, y: x == y,
        'iexact': lambda x, y: x.lower() == y.lower(),
        'contains': lambda x, y: y in x,
        'icontains': lambda x, y: y.lower() in x.lower(),
        'in': lambda x, y: x in y,
        'gt': lambda x, y: x > y,
        'gte': lambda x, y: x >= y,
        'lt': lambda x, y: x < y,
        'lte': lambda x, y: x > y,
        'startswith': lambda x, y: x.startswith(y),
        'istartswith': lambda x, y: x.lower().startswith(y.lower()),
        'endswith': lambda x, y: x.endswith(y),
        'iendswith': lambda x, y: x.lower().endswith(y.lower()),
        'range': lambda x, y: y[0] <= x <= y[1],
        'isnull': lambda x, y: x is None if y else x is not None,

        # XXX: compiling the regex on every invocation is slow
        'regex': lambda x, y: re.search(y, x),
        'iregex': lambda x, y: re.search(y, x, re.IGNORECASE),
    }

    def __init__(self, **kwargs):
        self.conditions = self.parse_conditions(kwargs)

    def __and__(self, other):
        if isinstance(other, Q):
            q = Q()
            q.conditions = self.conditions | other.conditions
            return q
        return super().__and__(other)

    def __repr__(self):
        conditions = []
        for field, op, value in self.conditions:
            conditions.append('{}__{}={!r}'.format(field, op, value))
        return 'Q({})'.format(', '.join(conditions))

    @classmethod
    def parse_conditions(cls, conditions):
        parsed = set()
        for key, value in conditions.items():
            field, sep, op = key.partition('__')
            if not sep:
                op = 'exact'
            parsed.add((field, op, value))
        return parsed

    def match(self, model, pk, obj_cache):
        pk_names = ('pk', model._meta.pk.attname)
        for field, op, value in self.conditions:
            op = self.OPERATORS[op]
            if field in pk_names and not op(pk, value):
                return False
            else:
                obj = obj_cache[pk]
                if not op(getattr(obj, field), value):
                    return False
        return True


class InvertedQ(Query):
    def __init__(self, subquery):
        self.subquery = subquery

    def __invert__(self):
        return self.subquery

    def __repr__(self):
        return '~{!r}'.format(self.subquery)

    def match(self, *args, **kwargs):
        return not self.subquery.match(*args, **kwargs)


class IntersectionQ(Query):
    def __init__(self, *subqueries):
        self.subqueries = subqueries

    def __and__(self, other):
        return IntersectionQ(other, *self.subqueries)

    def __repr__(self):
        r = ' & '.join('{!r}'.format(query) for query in self.subqueries)
        return '({})'.format(r)

    def match(self, *args, **kwargs):
        return all(query.match(*args, **kwargs) for query in self.subqueries)


class UnionQ(Query):
    def __init__(self, *subqueries):
        self.subqueries = subqueries

    def __or__(self, other):
        return UnionQ(other, *self.subqueries)

    def __repr__(self):
        r = ' | '.join('{!r}'.format(query) for query in self.subqueries)
        return '({})'.format(r)

    def match(self, *args, **kwargs):
        return any(query.match(*args, **kwargs) for query in self.subqueries)


class SliceQ(Query):
    def __init__(self, subquery, slice_):
        self.subquery = subquery
        self.slice = slice_

    def __repr__(self):
        bits = [self.slice.start, self.slice.stop]
        if self.slice.step:
            s.append(self.slice.step)
        bits = ['' if bit is None else str(bit) for bit in bits]
        return '{!r}[{}]'.format(self.subquery, ':'.join(bits))

    def execute(self, model, obj_cache=None):
        pks = self.subquery.execute(model, obj_cache=obj_cache)
        return islice(pks, self.slice.start, self.slice.stop, self.slice.step)
