import unittest

from tiget.testcases import GitTestCase
from tiget.git import models, init_repo


class Foo(models.Model):
    text = models.TextField()


class TestModelBase(GitTestCase):
    def setUp(self):
        super().setUp()
        init_repo()

    def test_exceptions(self):
        for exc_class in models.base.MODEL_EXCEPTIONS:
            model_exc_class = getattr(Foo, exc_class.__name__)
            self.assertTrue(issubclass(model_exc_class, exc_class))

    def test_storage_name(self):
        self.assertEqual(Foo._meta.storage_name, 'foos')

    def test_new(self):
        foo = Foo()
        self.assertEqual(foo.text, None)

    def test_new_with_argument(self):
        foo = Foo(text='foo')
        self.assertEqual(foo.text, 'foo')

    def test_new_with_invalid_argument(self):
        self.assertRaises(TypeError, Foo, bar='baz')

    def test_path_with_pk_none(self):
        foo = Foo(pk=None)
        self.assertRaises(ValueError, lambda: foo.path)

    def test_path(self):
        foo = Foo(text='')
        self.assertEqual(foo.path, ['foos', foo.id.hex])

    def test_save(self):
        self.assert_commit_count(1)
        foo = Foo(text='')
        foo.save()
        # TODO: test validations
        self.assert_commit_count(2)
        self.assert_file_exists('/'.join(foo.path))

    @unittest.skip('not implemented yet')
    def test_delete(self):
        pass

    def test_equality(self):
        foo = Foo(text='')
        foo.save()
        foo2 = Foo.objects.get(id=foo.id)
        self.assertEqual(foo, foo2)
