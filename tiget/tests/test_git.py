import shutil
from tempfile import mkdtemp
from subprocess import call, check_call, check_output

from nose.tools import ok_, eq_, raises, assert_raises

from tiget import git
from tiget.settings import settings
from tiget.git import init_repo, get_transaction, auto_transaction


class GitTestcase(object):
    def setup(self):
        self.repo = mkdtemp()
        settings.core.repository_path = self.repo
        check_call(['git', 'init', '--quiet'], cwd=self.repo)

    def teardown(self):
        git.repository_path = None
        shutil.rmtree(self.repo)

    def assert_file_exists(self, file):
        cmd = 'git ls-tree --name-only -r {} | grep -q ^{}$'.format(
            settings.core.branchname, file)
        check_call(cmd, cwd=self.repo, shell=True)

    def assert_commit_count(self, count):
        cmd = 'git log --oneline {} | wc -l'.format(settings.core.branchname)
        eq_(check_output(
            cmd, cwd=self.repo, shell=True).decode('utf-8'), str(count) + '\n')


class TestGit(GitTestcase):
    def test_init_repo(self):
        init_repo()
        ref = 'refs/heads/{}'.format(settings.core.branchname)
        check_call(
            ['git', 'show-ref', '--verify', '--quiet', ref], cwd=self.repo)
        self.assert_commit_count(1)
        self.assert_file_exists('config/VERSION')

    @auto_transaction()
    def test_get_transaction(self):
        with assert_raises(git.GitError):
            get_transaction(initialized=True)
        get_transaction(initialized=False)
        init_repo()
        get_transaction(initialized=True)
        with assert_raises(git.GitError):
            get_transaction(initialized=False)

    def test_transaction_commit(self):
        init_repo()
        with auto_transaction():
            transaction = get_transaction()
            transaction.set_blob('/foo', 'bar'.encode('utf-8'))
            transaction.add_message('foobar')
        self.assert_commit_count(2)
        self.assert_file_exists('foo')

    def test_transaction_rollback(self):
        class TestException(Exception): pass

        init_repo()
        with assert_raises(TestException):
            with auto_transaction():
                transaction = get_transaction()
                transaction.set_blob('/foo', 'bar'.encode('utf-8'))
                raise TestException()
        self.assert_commit_count(1)
