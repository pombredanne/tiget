import shutil
from tempfile import mkdtemp
from subprocess import call, check_call, check_output

from nose.tools import ok_, eq_, raises, assert_raises

from tiget.conf import settings
from tiget.git import transaction, init_repo, GitError


class GitTestcase(object):
    def setup(self):
        self.repo = mkdtemp()
        check_call(['git', 'init', '--quiet'], cwd=self.repo)
        settings.core.repository = self.repo
        self.branchref = 'refs/heads/{}'.format(settings.core.branchname)
        self.assert_commit_count(0)

    def teardown(self):
        shutil.rmtree(self.repo)

    def assert_file_exists(self, filename):
        cmd = 'git ls-tree --name-only -r {} | grep -q ^{}$'.format(
            self.branchref, filename)
        check_call(cmd, cwd=self.repo, shell=True)

    def assert_commit_count(self, count):
        cmd = 'git log --oneline {} 2>/dev/null| wc -l'.format(self.branchref)
        output = check_output(cmd, cwd=self.repo, shell=True).decode('utf-8')
        eq_(output.strip(), str(count))


class TestInitRepo(GitTestcase):
    def test_init_repo(self):
        init_repo()
        check_call(
            ['git', 'show-ref', '--verify', '--quiet', self.branchref],
            cwd=self.repo)
        self.assert_commit_count(1)
        self.assert_file_exists('config/VERSION')


class TestTransaction(GitTestcase):
    def test_commit(self):
        transaction.begin()
        trans = transaction.current(initialized=False)
        trans.set_blob(['foo'], 'bar'.encode('utf-8'))
        trans.add_message('foobar')
        self.assert_commit_count(0)
        transaction.commit()
        self.assert_commit_count(1)
        self.assert_file_exists('foo')

    def test_commit_nochanges(self):
        transaction.begin()
        self.assert_commit_count(0)
        with assert_raises(GitError):
            transaction.commit()
        self.assert_commit_count(0)
        transaction.rollback()

    def test_commmit_nomessage(self):
        transaction.begin()
        trans = transaction.current(initialized=False)
        trans.set_blob(['foo'], 'bar'.encode('utf-8'))
        self.assert_commit_count(0)
        with assert_raises(GitError):
            transaction.commit()
        self.assert_commit_count(0)
        transaction.rollback()

    def test_rollback(self):
        class TestException(Exception): pass

        with assert_raises(TestException):
            with transaction.wrap():
                trans = transaction.current(initialized=False)
                trans.set_blob(['foo'], 'bar'.encode('utf-8'))
                raise TestException()
        self.assert_commit_count(0)

    def test_transaction_current(self):
        with assert_raises(GitError):
            transaction.current(initialized=True)
        with assert_raises(GitError):
            transaction.current(initialized=False)
        with transaction.wrap():
            with assert_raises(GitError):
                transaction.current(initialized=True)
            transaction.current(initialized=False)
            init_repo()
            transaction.current(initialized=True)
            with assert_raises(GitError):
                transaction.current(initialized=False)


class TestTransactionWrap(GitTestcase):
    def test_wrap(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            trans.add_message('foobar')
            self.assert_commit_count(0)
        self.assert_commit_count(1)
        self.assert_file_exists('foo')

    def test_nochanges(self):
        with transaction.wrap():
            pass
        self.assert_commit_count(0)

    def test_exception(self):
        class TestException(Exception): pass

        with assert_raises(TestException):
            with transaction.wrap():
                trans = transaction.current(initialized=False)
                trans.set_blob(['foo'], 'bar'.encode('utf-8'))
                self.assert_commit_count(0)
                raise TestException()
        self.assert_commit_count(0)


class TestTransactionBlob(GitTestcase):
    def test_set_get(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            eq_(trans.get_blob(['foo']).decode('utf-8'), 'bar')
        self.assert_file_exists('foo')

    def test_set_get_separate_transactions(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
        self.assert_file_exists('foo')
        with transaction.wrap():
            trans = transaction.current()
            eq_(trans.get_blob(['foo']).decode('utf-8'), 'bar')
        self.assert_file_exists('foo')

    def test_exists(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            ok_(trans.exists(['foo']))

    def test_exists_separate_transaction(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            trans.add_message('dummy')
        with transaction.wrap():
            trans = transaction.current()
            ok_(trans.exists(['foo']))

    def test_list_blobs(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            ok_(trans.list_blobs([]) == set(['foo']))

    def test_list_blobs_separate_transaction(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            trans.add_message('dummy')
        with transaction.wrap():
            trans = transaction.current()
            ok_(trans.list_blobs([]) == set(['foo']))
