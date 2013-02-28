import sys
from importlib import import_module

from nose.tools import *

from tiget.testcases import GitTestCase
from tiget.git import transaction
from tiget.plugins import load_plugin, unload_plugin


def setup_module():
    load_plugin('tiget.git.importer')


def teardown_module():
    unload_plugin('importer')


def import_ok(name):
    mod = import_module(name)
    eq_(mod.ID, name)


def assert_import_fails(name):
    assert_raises(ImportError, import_module, name)


class TestImporter(GitTestCase):
    def teardown(self):
        for mod in list(sys.modules.keys()):
            if mod == 'foo' or mod.startswith('foo'):
                del sys.modules[mod]
        super().teardown()

    def create_file(self, path, id_):
        with transaction.wrap() as trans:
            trans.set_blob(
                path.lstrip('/').split('/'),
                'ID = {!r}'.format(id_).encode('utf-8'))
            trans.add_message('create file {}'.format(path))

    def test___import__(self):
        assert_import_fails('foo')
        self.create_file('/config/foo.py', 'foo')
        import_ok('foo')

    def test_import_package(self):
        assert_import_fails('foo')
        assert_import_fails('foo.bar')
        self.create_file('/config/foo/__init__.py', 'foo')
        self.create_file('/config/foo/bar.py', 'foo.bar')
        import_ok('foo')
        import_ok('foo.bar')

    def test___import___other_path(self):
        self.create_file('/somewhere/foo.py', 'foo')
        assert_import_fails('foo')
        sys.path.append('tiget-git-import:/somewhere')
        import_ok('foo')
        sys.path.remove('tiget-git-import:/somewhere')

    def test_non_existing(self):
        assert_import_fails('nix')


class TestImporterNotInitialized(GitTestCase):
    def test_non_existing(self):
        assert_raises(ImportError, import_module, 'nix')


class TestImporterNoRepository:
    def test_non_existing(self):
        assert_raises(ImportError, import_module, 'nix')
