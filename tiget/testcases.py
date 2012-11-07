import unittest
import shutil
from tempfile import mkdtemp
from subprocess import check_call, check_output

from tiget.conf import settings


class GitTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = mkdtemp()
        check_call(['git', 'init', '--quiet'], cwd=self.repo)
        settings.core.repository = self.repo
        self.branchref = 'refs/heads/{}'.format(settings.core.branchname)
        self.assert_commit_count(0)

    def tearDown(self):
        shutil.rmtree(self.repo)

    def assert_file_exists(self, filename):
        cmd = 'git ls-tree --name-only -r {} | grep -q ^{}$'.format(
            self.branchref, filename)
        check_call(cmd, cwd=self.repo, shell=True)

    def assert_commit_count(self, count):
        cmd = 'git log --oneline {} 2>/dev/null| wc -l'.format(self.branchref)
        output = check_output(cmd, cwd=self.repo, shell=True).decode('utf-8')
        self.assertEqual(output.strip(), str(count))
