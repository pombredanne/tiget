from subprocess import check_call

from tiget.testcases import GitTestCase
from tiget.git import init_repo, GitError


class TestInitRepo(GitTestCase):
    def test_init_repo(self):
        init_repo()
        check_call(['git', 'show-ref', '--verify', '--quiet', self.branchref],
            cwd=self.repo)
        self.assert_commit_count(1)
        self.assert_file_exists('config/VERSION')

    def test_already_initialized(self):
        init_repo()
        self.assertRaises(GitError, init_repo)
