import unittest
import shutil
from tempfile import mkdtemp
import stat

import pygit2

from tiget.conf import settings


class GitTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = pygit2.init_repository(mkdtemp(), False)
        settings.core.repository = self.repo.path
        self.branchref = 'refs/heads/{}'.format(settings.core.branchname)
        self.assert_commit_count(0)

    def tearDown(self):
        shutil.rmtree(self.repo.workdir)

    def assert_file_exists(self, filename):
        try:
            oid = self.repo.lookup_reference(self.branchref).oid
        except KeyError:
            self.fail('{} does not exist'.format(self.branchref))
        tree = self.repo[oid].tree
        *path, filename = filename.split('/')
        while path:
            name = path.pop()
            self.assertIn(name, tree)
            entry = tree[name]
            if not entry.attributes & stat.S_IFDIR:
                self.fail('{} is not a directory'.format(name))
            tree = entry.to_object()
        self.assertIn(filename, tree)
        entry = tree[filename]
        self.assertTrue(entry.attributes & stat.S_IFREG)

    def assert_commit_count(self, expected_count):
        try:
            oid = self.repo.lookup_reference(self.branchref).oid
        except KeyError:
            count = 0
        else:
            count = sum(1 for _ in self.repo.walk(oid, pygit2.GIT_SORT_NONE))
        self.assertEqual(count, expected_count)
