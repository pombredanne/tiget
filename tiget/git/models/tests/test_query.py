from itertools import combinations
from random import choice

from nose.tools import *

from tiget.git.models.query import Query, Q, Inversion, Intersection, Union, Slice


def generate_conditions():
    operators = Q.OPERATORS.keys()
    for i in range(3):
        for ops in combinations(operators, i):
            d = {}
            for op in ops:
                field_name = choice(('foo', 'bar', 'baz'))
                lookup = '{}__{}'.format(field_name, op) if op else field_name
                d[lookup] = 42
            yield d


class TestQ(object):
    def test_equality(self):
        for conditions in generate_conditions():
            eq_(Q(**conditions), Q(**conditions))

    def test_inequality(self):
        cond = iter(generate_conditions())
        for conditions1, conditions2 in zip(cond, cond):
            assert_not_equal(Q(**conditions1), Q(**conditions2))

    def test_repr(self):
        for conditions in generate_conditions():
            q = Q(**conditions)
            eq_(q, eval(repr(q)))


class TestInversion(object):
    def test_equality(self):
        for conditions in generate_conditions():
            q = Q(**conditions)
            eq_(Inversion(q), Inversion(q))

    def test_inequality(self):
        cond = iter(generate_conditions())
        for conditions1, conditions2 in zip(cond, cond):
            assert_not_equal(~Q(**conditions1), ~Q(**conditions2))

    def test_repr(self):
        for conditions in generate_conditions():
            q = ~Q(**conditions)
            eq_(q, eval(repr(q)))


class TestIntersection(object):
    def test_equality(self):
        cond = iter(generate_conditions())
        for conditions1, conditions2 in zip(cond, cond):
            qs = (Q(**conditions1), Q(**conditions2))
            eq_(Intersection(*qs), Intersection(*qs))

    def test_inequality(self):
        cond = iter(generate_conditions())
        cond = iter(zip(cond, cond))
        for conditions1, conditions2 in zip(cond, cond):
            qs1 = (Q(**conditions1[0]), Q(**conditions1[1]))
            qs2 = (Q(**conditions2[0]), Q(**conditions2[1]))
            assert_not_equal(Intersection(*qs1), Intersection(*qs2))

    def test_repr(self):
        cond = iter(generate_conditions())
        for conditions1, conditions2 in zip(cond, cond):
            q = Q(**conditions1) | Q(**conditions2)
            eq_(q, eval(repr(q)))


class TestUnion(object):
    def test_equality(self):
        cond = iter(generate_conditions())
        for conditions1, conditions2 in zip(cond, cond):
            qs = (Q(**conditions1), Q(**conditions2))
            eq_(Union(*qs), Union(*qs))

    def test_inequality(self):
        cond = iter(generate_conditions())
        cond = iter(zip(cond, cond))
        for conditions1, conditions2 in zip(cond, cond):
            qs1 = (Q(**conditions1[0]), Q(**conditions1[1]))
            qs2 = (Q(**conditions2[0]), Q(**conditions2[1]))
            assert_not_equal(Union(*qs1), Union(*qs2))

    def test_repr(self):
        cond = iter(generate_conditions())
        for conditions1, conditions2 in zip(cond, cond):
            q = Q(**conditions1) & Q(**conditions2)
            eq_(q, eval(repr(q)))


class TestSlice(object):
    def test_equality(self):
        for s in ((None,), (0,), (0, 3), (0, 3, 2)):
            eq_(Slice(Q(), slice(*s)), Slice(Q(), slice(*s)))

    def test_inequality(self):
        args = iter(((None,), (0,), (0, 3), (0, 3, 2)))
        for s1, s2 in zip(args, args):
            assert_not_equal(Slice(Q(), slice(*s1)), Slice(Q(), slice(*s2)))

    def test_repr(self):
        for s in ((None,), (0,), (0, 3), (0, 3, 2)):
            q = Q().__getitem__(slice(*s))
            eq_(q, eval(repr(q)))


class TestOperators(object):
    def test_union(self):
        a, b = Query(), Query()
        q = a | b
        assert_is_instance(q, Union)
        assert_set_equal(q.subqueries, set((a, b)))

    def test_intersection(self):
        a, b = Query(), Query()
        q = a & b
        assert_is_instance(q, Intersection)
        assert_set_equal(q.subqueries, set((a, b)))

    def test_inversion(self):
        q = Query()
        assert_is_instance(~q, Inversion)
        eq_((~q).subquery, q)


class TestUnionOptimizations(object):
    def check_both(self, a, b, result):
        eq_(a | b, result)
        eq_(b | a, result)

    def test_with_everything(self):
        self.check_both(Q(), Query(), Q())

    def test_with_nothing(self):
        q = Query()
        self.check_both(~Q(), q, q)

    def test_query_with_its_inversion(self):
        q = Query()
        self.check_both(q, ~q, Q())

    def test_query_with_union(self):
        a, b, c = Query(), Query(), Query()
        self.check_both(a | b, c, Union(a, b, c))

    def test_union_with_union(self):
        a, b, c, d = Query(), Query(), Query(), Query()
        self.check_both(a | b, c | d, Union(a, b, c, d))


class TestIntersectionOptimizations(object):
    def check_both(self, a, b, result):
        eq_(a & b, result)
        eq_(b & a, result)

    def test_intersection_everything(self):
        q = Query()
        self.check_both(Q(), q, q)

    def test_intersection_nothing(self):
        self.check_both(~Q(), Query(), ~Q())

    def test_intersection_query_with_its_inversion(self):
        q = Query()
        self.check_both(q, ~q, ~Q())

    def test_query_with_intersection(self):
        a, b, c = Query(), Query(), Query()
        self.check_both(a & b, c, Intersection(a, b, c))

    def test_intersection_with_intersection(self):
        a, b, c, d = Query(), Query(), Query(), Query()
        self.check_both(a & b, c & d, Intersection(a, b, c, d))

    def test_q_intersection(self):
        q = Q(foo=42) & Q(bar=42)
        eq_(q, Q(foo=42, bar=42))
        assert_is_instance(q, Q)


class TestInversionOptimizations(object):
    def test_inversion_inversion(self):
        q = Q(foo=42)
        assert_is(~~q, q)
