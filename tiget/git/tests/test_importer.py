import sys

from nose.tools import *

from tiget.testcases import GitTestCase
from tiget.git import transaction, init_repo


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
    def setup(self):
        super().setup()
        init_repo()

    def teardown(self):
        for mod in list(sys.modules.keys()):
            if mod == 'foo' or mod.startswith('foo'):
                del sys.modules[mod]
        super().teardown()

    def test_import_module(self):
        with transaction.wrap():
            assert_raises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(['config', 'foo.py'], TEST_MODULE.encode('utf-8'))
            trans.add_message('foo')
            import foo
            eq_(foo.foo(), 'foo')

    def test_import_module_separate_transaction(self):
        with transaction.wrap():
            assert_raises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(['config', 'foo.py'], TEST_MODULE.encode('utf-8'))
            trans.add_message('foo')
        import foo
        eq_(foo.foo(), 'foo')

    def test_import_package(self):
        with transaction.wrap():
            assert_raises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(
                ['config', 'foo', '__init__.py'],
                TEST_PACKAGE_INIT_PY.encode('utf-8'))
            trans.set_blob(
                ['config', 'foo', 'bar.py'],
                TEST_PACKAGE_BAR_PY.encode('utf-8'))
            trans.add_message('foo')
            import foo
            eq_(foo.foo(), 'foo')
            from foo import bar
            eq_(bar.bar(), 'bar')

    def test_import_package_separate_transaction(self):
        with transaction.wrap():
            assert_raises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(
                ['config', 'foo', '__init__.py'],
                TEST_PACKAGE_INIT_PY.encode('utf-8'))
            trans.set_blob(
                ['config', 'foo', 'bar.py'],
                TEST_PACKAGE_BAR_PY.encode('utf-8'))
            trans.add_message('foo')
        import foo
        eq_(foo.foo(), 'foo')
        from foo import bar
        eq_(bar.bar(), 'bar')

    def test_import_module_other_path(self):
        with transaction.wrap():
            assert_raises(ImportError, __import__, 'foo')
            trans = transaction.current()
            trans.set_blob(['foo', 'foo.py'], TEST_MODULE.encode('utf-8'))
            trans.add_message('foo')
            sys.path.append('tiget-git-import:/foo')
            import foo
            eq_(foo.foo(), 'foo')
            sys.path.remove('tiget-git-import:/foo')


class TestImporterNotInitialized(GitTestCase):
    def test_import_module(self):
        with assert_raises(ImportError):
            import doesnotexist

    def test_import_package(self):
        with assert_raises(ImportError):
            from doesnotexist import foo
