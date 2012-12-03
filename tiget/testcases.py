import shutil
import stat
from tempfile import mkdtemp

from nose.tools import *
import pygit2

from tiget.conf import settings


class GitTestCase:
    def setup(self):
        self.repo = pygit2.init_repository(mkdtemp(), False)
        settings.core.repository = self.repo.path
        self.branchref = 'refs/heads/{}'.format(settings.core.branchname)
        self.assert_commit_count(0)

    def teardown(self):
        shutil.rmtree(self.repo.workdir)

    def assert_file_exists(self, filename):
        oid = self.repo.lookup_reference(self.branchref).oid
        tree = self.repo[oid].tree
        *path, filename = filename.split('/')
        for name in path:
            assert_in(name, tree)
            entry = tree[name]
            ok_(entry.attributes & stat.S_IFDIR)
            tree = entry.to_object()
        assert_in(filename, tree)
        entry = tree[filename]
        ok_(entry.attributes & stat.S_IFREG)

    def assert_commit_count(self, expected_count):
        try:
            oid = self.repo.lookup_reference(self.branchref).oid
        except KeyError:
            count = 0
        else:
            count = sum(1 for _ in self.repo.walk(oid, pygit2.GIT_SORT_NONE))
        eq_(count, expected_count)
