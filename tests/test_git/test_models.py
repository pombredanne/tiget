from tiget.testcases import GitTestCase
from tiget.git import models, init_repo


class User(models.Model):
    name = models.TextField()


class Ticket(models.Model):
    title = models.TextField()


class TestModelBase(GitTestCase):
    def setUp(self):
        super().setUp()
        init_repo()

    def test_exceptions(self):
        for exc_class in models.base.MODEL_EXCEPTIONS:
            model_exc_class = getattr(Ticket, exc_class.__name__)
            self.assertTrue(issubclass(model_exc_class, exc_class))

    def test_storage_name(self):
        self.assertEqual(Ticket._meta.storage_name, 'tickets')

    def test_new(self):
        ticket = Ticket()
        self.assertEqual(ticket.title, None)

    def test_new_with_argument(self):
        ticket = Ticket(title='test ticket')
        self.assertEqual(ticket.title, 'test ticket')

    def test_new_with_invalid_argument(self):
        self.assertRaises(TypeError, Ticket, bar='baz')

    def test_path_with_pk_none(self):
        ticket = Ticket(pk=None)
        self.assertRaises(ValueError, lambda: ticket.path)

    def test_path(self):
        ticket = Ticket(title='')
        self.assertEqual(ticket.path, ['tickets', ticket.id.hex])

    def test_save(self):
        self.assert_commit_count(1)
        ticket = Ticket(title='')
        ticket.save()
        # TODO: test validations
        self.assert_commit_count(2)
        self.assert_file_exists('/'.join(ticket.path))

    def test_delete(self):
        self.skipTest('not implemented yet')

    def test_equality(self):
        ticket = Ticket()
        ticket2 = Ticket(id=ticket.id)
        self.assertEqual(ticket, ticket2)

    def test_equality_unequal(self):
        self.assertNotEqual(Ticket(), Ticket())

    def test_equality_other_model(self):
        self.assertNotEqual(Ticket(), User())


class TestManager(GitTestCase):
    def setUp(self):
        super().setUp()
        init_repo()

    def test_filter(self):
        ticket = Ticket.objects.create(title='test ticket')
        self.assertEqual(len(list(Ticket.objects.filter())), 1)
        self.assertEqual(len(list(Ticket.objects.filter(title='foo'))), 0)
        self.assertEqual(
            len(list(Ticket.objects.filter(title='test ticket'))), 1)

    def test_all(self):
        ticket = Ticket.objects.create(title='test ticket')
        self.assertEqual(len(list(Ticket.objects.all())), 1)

    def test_get(self):
        ticket = Ticket.objects.create(title='test ticket')
        ticket = Ticket.objects.get(id=ticket.id)
        self.assertEqual(ticket.title, 'test ticket')
        self.assertRaises(Ticket.DoesNotExist, Ticket.objects.get, title='foo')
        Ticket.objects.create(title='test ticket')
        self.assertRaises(Ticket.MultipleObjectsReturned, Ticket.objects.get,
            title='test ticket')

    def test_exists(self):
        self.assertFalse(Ticket.objects.exists(title='test ticket'))
        Ticket.objects.create(title='test ticket')
        self.assertTrue(Ticket.objects.exists(title='test ticket'))

    def test_count(self):
        self.assertEqual(Ticket.objects.count(), 0)
        for i in range(1, 11):
            Ticket.objects.create(title='test ticket')
            self.assertEqual(Ticket.objects.count(), i)

    def test_order_by(self):
        self.skipTest('not implemented yet')

    def test_create(self):
        ticket = Ticket.objects.create(title='test ticket')
        self.assert_commit_count(2)
        self.assert_file_exists('/'.join(ticket.path))
