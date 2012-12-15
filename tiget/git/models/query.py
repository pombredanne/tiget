import re

from tiget.git import transaction


class Query:
    def __or__(self, other):
        for a, b in ((self, other), (other, self)):
            if a == Q():
                return a
            elif a == ~Q():
                return b
            elif isinstance(a, Inversion) and a.subquery == b:
                return Q()
            elif isinstance(a, Union) and not isinstance(b, Union):
                return Union(b, *a.subqueries)
        if isinstance(self, Union) and isinstance(other, Union):
            return Union(*(self.subqueries | other.subqueries))
        return Union(self, other)

    def __and__(self, other):
        for a, b in ((self, other), (other, self)):
            if a == Q():
                return b
            elif a == ~Q():
                return a
            elif isinstance(a, Inversion) and a.subquery == b:
                return ~Q()
            elif isinstance(a, Intersection) and not isinstance(b, Intersection):
                return Intersection(b, *a.subqueries)
        if isinstance(self, Intersection) and isinstance(other, Intersection):
            return Intersection(*(self.subqueries | other.subqueries))
        elif isinstance(self, Q) and isinstance(other, Q):
            q = Q()
            q.conditions = self.conditions | other.conditions
            return q
        return Intersection(self, other)

    def __invert__(self):
        if isinstance(self, Inversion):
            return self.subquery
        return Inversion(self)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Slice(self, key)
        raise TypeError('index must be a slice')

    def __ne__(self, other):
        # __eq__ has to be implemented for every subclass separately
        return not self == other

    def order_by(self, *order_by):
        return Ordered(self, *order_by)

    def execute(self, obj_cache, pks):
        raise NotImplementedError


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

    def match(self, pk, obj_cache):
        pk_names = ('pk', obj_cache.model._meta.pk.attname)
        for field, op, value in self.conditions:
            op = self.OPERATORS[op]
            if field in pk_names and not op(pk, value):
                return False
            else:
                obj = obj_cache[pk]
                if not op(getattr(obj, field), value):
                    return False
        return True

    def execute(self, obj_cache, pks):
        return [pk for pk in pks if self.match(pk, obj_cache)]


class Inversion(Query):
    def __init__(self, subquery):
        self.subquery = subquery

    def __repr__(self):
        return '~{!r}'.format(self.subquery)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subquery == other.subquery)

    def __hash__(self):
        return hash(self.subquery)

    def execute(self, obj_cache, pks):
        matched = self.subquery.execute(obj_cache, pks)
        return [pk for pk in pks if not pk in matched]


class Intersection(Query):
    def __init__(self, *subqueries):
        self.subqueries = frozenset(subqueries)

    def __repr__(self):
        bits = (repr(query) for query in self.subqueries)
        return '({})'.format(' & '.join(bits))

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subqueries == other.subqueries)

    def __hash__(self):
        return hash(self.subqueries)

    def execute(self, obj_cache, pks):
        for subquery in self.subqueries:
            pks = subquery.execute(obj_cache, pks)
        return pks


class Union(Query):
    def __init__(self, *subqueries):
        self.subqueries = frozenset(subqueries)

    def __repr__(self):
        bits = (repr(query) for query in self.subqueries)
        return '({})'.format(' | '.join(bits))

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subqueries == other.subqueries)

    def __hash__(self):
        return hash(self.subqueries)

    def execute(self, obj_cache, pks):
        pks = set(pks)
        result = []
        for subquery in self.subqueries:
            result += subquery.execute(obj_cache, pks)
            pks.difference_update(result)
        return result


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

    def execute(self, obj_cache, pks):
        return self.subquery.execute(obj_cache, pks)[self.slice]


class Ordered(Query):
    def __init__(self, subquery, *order_by):
        self.subquery = subquery
        self.order_by = order_by

    def __repr__(self):
        bits = (repr(bit) for bit in self.order_by)
        return '{!r}.order_by({})'.format(self.subquery, ', '.join(bits))

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
            self.subquery == other.subquery and self.order_by == other.order_by)

    def __hash__(self):
        return hash((self.subquery, self.order_by))

    def execute(self, obj_cache, pks):
        pks = self.subquery.execute(obj_cache, pks)
        pk_names = ('pk', obj_cache.model._meta.pk.attname)
        for field in reversed(self.order_by):
            reverse = False
            if field.startswith('-'):
                field = field[1:]
                reverse = True
            if field in pk_names:
                pks.sort(reverse=reverse)
                continue

            def _key(pk):
                return getattr(obj_cache[pk], field)
            keys = [_key(pk) for pk in pks]
            key_null = []
            i = 0
            while True:
                try:
                    keys.index(None, i)
                except ValueError:
                    break
                del keys[i]
                key_null.append(pks.pop(i))
            pks.sort(key=_key, reverse=reverse)
            if reverse:
                pks.extend(key_null)
            else:
                for i, pk in enumerate(key_null):
                    pks.insert(i, pk)
        return pks
