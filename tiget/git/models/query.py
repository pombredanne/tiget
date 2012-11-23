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
            if a == Q():
                return a
            elif a == ~Q():
                return b
            elif (isinstance(a, Inversion) and a.subquery == b):
                return Q()
        if isinstance(self, Union) and isinstance(other, Union):
            return Union(*(self.subqueries | other.subqueries))
        return Union(self, other)

    def __and__(self, other):
        for a, b in ((self, other), (other, self)):
            if a == Q():
                return b
            elif a == ~Q():
                return a
            elif (isinstance(a, Inversion) and a.subquery == b):
                return ~Q()
        if isinstance(self, Intersection) and isinstance(other, Intersection):
            return Intersection(*(self.subqueries | other.subqueries))
        return Intersection(self, other)

    def __invert__(self):
        return Inversion(self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Slice(self, key)
        raise TypeError('index must be a slice')

    def __ne__(self, other):
        # __eq__ has to be implemented for every subclass separately
        return not self == other

    def match(self, model, pk, obj_cache):
        raise NotImplementedError

    def execute(self, model, obj_cache=None):
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
        conditions = set()
        for key, value in kwargs.items():
            field, sep, op = key.partition('__')
            if not sep:
                op = 'exact'
            conditions.add((field, op, value))
        self.conditions = frozenset(conditions)

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

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.conditions == other.conditions)

    def __hash__(self):
        return hash(self.conditions)

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


class Inversion(Query):
    def __init__(self, subquery):
        self.subquery = subquery

    def __invert__(self):
        return self.subquery

    def __repr__(self):
        return '~{!r}'.format(self.subquery)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subquery == other.subquery)

    def __hash__(self):
        return hash(self.subquery)

    def match(self, *args, **kwargs):
        return not self.subquery.match(*args, **kwargs)


class Intersection(Query):
    def __init__(self, *subqueries):
        self.subqueries = frozenset(subqueries)

    def __and__(self, other):
        return Intersection(other, *self.subqueries)

    def __repr__(self):
        r = ' & '.join(repr(query) for query in self.subqueries)
        return '({})'.format(r)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subqueries == other.subqueries)

    def __hash__(self):
        return hash(self.subqueries)

    def match(self, *args, **kwargs):
        return all(query.match(*args, **kwargs) for query in self.subqueries)


class Union(Query):
    def __init__(self, *subqueries):
        self.subqueries = frozenset(subqueries)

    def __or__(self, other):
        return Union(other, *self.subqueries)

    def __repr__(self):
        r = ' | '.join(repr(query) for query in self.subqueries)
        return '({})'.format(r)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subqueries == other.subqueries)

    def __hash__(self):
        return hash(self.subqueries)

    def match(self, *args, **kwargs):
        return any(query.match(*args, **kwargs) for query in self.subqueries)


class Slice(Query):
    def __init__(self, subquery, slice_):
        self.subquery = subquery
        self.slice = slice_

    def __repr__(self):
        bits = [self.slice.start, self.slice.stop]
        if self.slice.step:
            bits.append(self.slice.step)
        bits = ['' if bit is None else str(bit) for bit in bits]
        return '{!r}[{}]'.format(self.subquery, ':'.join(bits))

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subquery == other.subquery and self.slice == other.slice)

    def __hash__(self):
        # cheat python into hashing a slice, queries are immutable anyway
        slice_ = (self.slice.start, self.slice.stop, self.slice.step)
        return hash((self.subquery, slice_))

    def execute(self, model, obj_cache=None):
        pks = self.subquery.execute(model, obj_cache=obj_cache)
        return islice(pks, self.slice.start, self.slice.stop, self.slice.step)
