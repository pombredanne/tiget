from nose.tools import *
from nose.plugins.skip import SkipTest

from tiget.testcases import GitTestCase
from tiget.git import models, init_repo


class Ticket(models.Model):
    title = models.TextField()
    description = models.TextField(null=True)


class TestQueryset(GitTestCase):
    def setup(self):
        super().setup()
        init_repo()

    def test_repr(self):
        raise SkipTest('test not written yet.')

    def test_or(self):
        raise SkipTest('test not written yet.')

    def test_and(self):
        raise SkipTest('test not written yet.')

    def test_invert(self):
        raise SkipTest('test not written yet.')

    def test_getitem(self):
        raise SkipTest('test not written yet.')

    def test_iter(self):
        raise SkipTest('test not written yet.')

    def test_all(self):
        ticket = Ticket.create(title='test ticket')
        eq_(len(list(Ticket.objects.all())), 1)

    def test_filter(self):
        # TODO: test with args and/or kwargs
        ticket = Ticket.create(title='test ticket')
        eq_(len(list(Ticket.objects.filter())), 1)
        eq_(len(list(Ticket.objects.filter(title='foo'))), 0)
        eq_(len(list(Ticket.objects.filter(title='test ticket'))), 1)

    def test_exclude(self):
        raise SkipTest('test not written yet.')

    def test_get(self):
        # TODO: test with args and/or kwargs
        ticket = Ticket.create(title='test ticket')
        ticket = Ticket.objects.get(id=ticket.id)
        eq_(ticket.title, 'test ticket')
        assert_raises(Ticket.DoesNotExist, Ticket.objects.get, title='foo')
        Ticket.create(title='test ticket')
        assert_raises(Ticket.MultipleObjectsReturned, Ticket.objects.get,
            title='test ticket')

    def test_exists(self):
        # TODO: test with args and/or kwargs
        assert_false(Ticket.objects.exists(title='test ticket'))
        Ticket.create(title='test ticket')
        ok_(Ticket.objects.exists(title='test ticket'))

    def test_count(self):
        # TODO: test with args and/or kwargs
        eq_(Ticket.objects.count(), 0)
        for i in range(1, 11):
            Ticket.create(title='test ticket')
            eq_(Ticket.objects.count(), i)

    def test_order_by(self):
        # TODO: test with more than one argument
        ascending = [str(i) for i in range(10)]
        descending = list(reversed(ascending))
        for title, description in zip(ascending, descending):
            Ticket.create(title=title, description=description)
        eq_([t.title for t in Ticket.objects.order_by('title')], ascending)
        eq_([t.title for t in Ticket.objects.order_by('-title')], descending)
        eq_([t.description for t in Ticket.objects.order_by('description')], ascending)
        eq_([t.description for t in Ticket.objects.order_by('-description')], descending)

        t = Ticket.create(title='10', description=None)
        eq_(Ticket.objects.order_by('description')[0], t)
        eq_(Ticket.objects.order_by('-description')[-1], t)
