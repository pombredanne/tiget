from nose.tools import *
from nose.plugins.skip import SkipTest

from tiget.testcases import GitTestCase
from tiget.git import models, init_repo


class Ticket(models.Model):
    title = models.TextField()


class TestManager(GitTestCase):
    def setup(self):
        super().setup()
        init_repo()

    def test_filter(self):
        ticket = Ticket.objects.create(title='test ticket')
        eq_(len(list(Ticket.objects.filter())), 1)
        eq_(len(list(Ticket.objects.filter(title='foo'))), 0)
        eq_(len(list(Ticket.objects.filter(title='test ticket'))), 1)

    def test_all(self):
        ticket = Ticket.objects.create(title='test ticket')
        eq_(len(list(Ticket.objects.all())), 1)

    def test_get(self):
        ticket = Ticket.objects.create(title='test ticket')
        ticket = Ticket.objects.get(id=ticket.id)
        eq_(ticket.title, 'test ticket')
        assert_raises(Ticket.DoesNotExist, Ticket.objects.get, title='foo')
        Ticket.objects.create(title='test ticket')
        assert_raises(Ticket.MultipleObjectsReturned, Ticket.objects.get,
            title='test ticket')

    def test_exists(self):
        assert_false(Ticket.objects.exists(title='test ticket'))
        Ticket.objects.create(title='test ticket')
        ok_(Ticket.objects.exists(title='test ticket'))

    def test_count(self):
        eq_(Ticket.objects.count(), 0)
        for i in range(1, 11):
            Ticket.objects.create(title='test ticket')
            eq_(Ticket.objects.count(), i)

    def test_order_by(self):
        raise SkipTest('not implemented yet')

    def test_create(self):
        ticket = Ticket.objects.create(title='test ticket')
        self.assert_commit_count(2)
        self.assert_file_exists('/'.join(ticket.path))
