
from tiget.testcases import GitTestCase
from tiget.git import transaction, init_repo, GitError


class TestTransaction(GitTestCase):
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
        self.assertRaises(GitError, transaction.commit)
        self.assert_commit_count(0)
        transaction.rollback()

    def test_commmit_nomessage(self):
        transaction.begin()
        trans = transaction.current(initialized=False)
        trans.set_blob(['foo'], 'bar'.encode('utf-8'))
        self.assert_commit_count(0)
        self.assertRaises(GitError, transaction.commit)
        self.assert_commit_count(0)
        transaction.rollback()

    def test_rollback(self):
        class TestException(Exception): pass

        def _foo():
            with transaction.wrap():
                trans = transaction.current(initialized=False)
                trans.set_blob(['foo'], 'bar'.encode('utf-8'))
                raise TestException()
        self.assertRaises(TestException, _foo)
        self.assert_commit_count(0)

    def test_transaction_current(self):
        self.assertRaises(GitError, transaction.current, initialized=True)
        self.assertRaises(GitError, transaction.current, initialized=False)
        with transaction.wrap():
            self.assertRaises(GitError, transaction.current, initialized=True)
            transaction.current(initialized=False)
            init_repo()
            transaction.current(initialized=True)
            self.assertRaises(GitError, transaction.current, initialized=False)


class TestTransactionWrap(GitTestCase):
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

        def _foo():
            with transaction.wrap():
                trans = transaction.current(initialized=False)
                trans.set_blob(['foo'], 'bar'.encode('utf-8'))
                self.assert_commit_count(0)
                raise TestException()
        self.assertRaises(TestException, _foo)
        self.assert_commit_count(0)


class TestTransactionBlob(GitTestCase):
    def test_set_get(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            self.assertEqual(trans.get_blob(['foo']).decode('utf-8'), 'bar')
        self.assert_file_exists('foo')

    def test_set_get_separate_transactions(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
        self.assert_file_exists('foo')
        with transaction.wrap():
            trans = transaction.current()
            self.assertEqual(trans.get_blob(['foo']).decode('utf-8'), 'bar')
        self.assert_file_exists('foo')

    def test_exists(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            self.assertTrue(trans.exists(['foo']))

    def test_exists_separate_transaction(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            trans.add_message('dummy')
        with transaction.wrap():
            trans = transaction.current()
            self.assertTrue(trans.exists(['foo']))

    def test_list_blobs(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.add_message('dummy')
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            self.assertEqual(trans.list_blobs([]), set(['foo']))

    def test_list_blobs_separate_transaction(self):
        with transaction.wrap():
            trans = transaction.current(initialized=False)
            trans.set_blob(['foo'], 'bar'.encode('utf-8'))
            trans.add_message('dummy')
        with transaction.wrap():
            trans = transaction.current()
            self.assertEqual(trans.list_blobs([]), set(['foo']))
