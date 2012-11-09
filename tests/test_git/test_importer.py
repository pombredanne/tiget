import sys

from tiget.testcases import GitTestCase
from tiget.git import transaction, init_repo
from tiget.plugins import load_plugin, unload_plugin


TEST_MODULE = """
def foo():
    return 'foo'
"""


TEST_PACKAGE_INIT_PY = """
def foo():
    return 'foo'
"""

TEST_PACKAGE_BAR_PY = """
def bar():
    return 'bar'
"""


class TestImporter(GitTestCase):
    def setUp(self):
        super().setUp()
        init_repo()
        load_plugin('importer')

    def tearDown(self):
        for mod in list(sys.modules.keys()):
            if mod == 'foo' or mod.startswith('foo'):
                del sys.modules[mod]
        unload_plugin('importer')
        super().tearDown()

    def test_import_module(self):
        with transaction.wrap():
            self.assertRaises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(['config', 'foo.py'], TEST_MODULE.encode('utf-8'))
            trans.add_message('foo')
            import foo
            self.assertEqual(foo.foo(), 'foo')

    def test_import_module_separate_transaction(self):
        with transaction.wrap():
            self.assertRaises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(['config', 'foo.py'], TEST_MODULE.encode('utf-8'))
            trans.add_message('foo')
        import foo
        self.assertEqual(foo.foo(), 'foo')

    def test_import_package(self):
        with transaction.wrap():
            self.assertRaises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(
                ['config', 'foo', '__init__.py'],
                TEST_PACKAGE_INIT_PY.encode('utf-8'))
            trans.set_blob(
                ['config', 'foo', 'bar.py'],
                TEST_PACKAGE_BAR_PY.encode('utf-8'))
            trans.add_message('foo')
            import foo
            self.assertEqual(foo.foo(), 'foo')
            from foo import bar
            self.assertEqual(bar.bar(), 'bar')

    def test_import_package_separate_transaction(self):
        with transaction.wrap():
            self.assertRaises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(
                ['config', 'foo', '__init__.py'],
                TEST_PACKAGE_INIT_PY.encode('utf-8'))
            trans.set_blob(
                ['config', 'foo', 'bar.py'],
                TEST_PACKAGE_BAR_PY.encode('utf-8'))
            trans.add_message('foo')
        import foo
        self.assertEqual(foo.foo(), 'foo')
        from foo import bar
        self.assertEqual(bar.bar(), 'bar')

    def test_import_module_other_path(self):
        with transaction.wrap():
            self.assertRaises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(['foo', 'foo.py'], TEST_MODULE.encode('utf-8'))
            trans.add_message('foo')
            sys.path.append('tiget-git-import:/foo')
            import foo
            self.assertEqual(foo.foo(), 'foo')
            sys.path.remove('tiget-git-import:/foo')
