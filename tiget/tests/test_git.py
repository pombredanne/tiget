from nose.tools import ok_, eq_, raises, assert_raises
import shutil
from tempfile import mkdtemp
from subprocess import call, check_call, check_output
from tiget import settings, git
from tiget.git import init_repo, get_transaction, auto_transaction

class GitTestcase(object):
    def setup(self):
        self.repo = mkdtemp()
        git.repository_path = self.repo
        check_call(['git', 'init', '--quiet'], cwd=self.repo)

    def teardown(self):
        git.repository_path = None
        shutil.rmtree(self.repo)

    def assert_file_exists(self, file):
        cmd = 'git ls-tree --name-only -r {0} | grep -q ^{1}$'.format(
            settings.branchname, file)
        check_call(cmd, cwd=self.repo, shell=True)

    def assert_commit_count(self, count):
        cmd = 'git log --oneline {0} | wc -l'.format(settings.branchname)
        eq_(check_output(cmd, cwd=self.repo, shell=True), str(count)+'\n')

class TestGit(GitTestcase):
    def test_init_repo(self):
        init_repo()
        ref = 'refs/heads/{0}'.format(settings.branchname)
        check_call(['git', 'show-ref', '--verify', '--quiet', ref], cwd=self.repo)
        self.assert_commit_count(1)
        self.assert_file_exists('VERSION')

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
            transaction['/foo'] = u'bar'
            transaction.add_message(u'foobar')
        self.assert_commit_count(2)
        self.assert_file_exists('foo')

    def test_transaction_rollback(self):
        init_repo()
        class TestException(Exception): pass
        with assert_raises(TestException):
            with auto_transaction():
                transaction = get_transaction()
                transaction['/foo'] = u'bar'
                raise TestException()
        self.assert_commit_count(1)
