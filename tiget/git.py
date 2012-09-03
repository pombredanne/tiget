import os
import stat
import time
from functools import wraps

from dulwich.objects import Blob, Tree, Commit
from dulwich.repo import Repo, NotGitRepository

from tiget import get_version
from tiget import settings

transaction = None
repository_path = None


class GitError(Exception):
    pass


def get_transaction(initialized=True):
    if initialized and not transaction.is_initialized:
        raise GitError('repository is not initialized')
    elif not initialized and transaction.is_initialized:
        raise GitError('repository is initialized')
    return transaction


class Transaction(object):
    def __init__(self):
        try:
            repo = Repo(repository_path or os.getcwd())
        except NotGitRepository:
            raise GitError('no git repository found')
        self.repo = repo
        self.ref = 'refs/heads/{0}'.format(settings.branchname)
        try:
            previous_commit_id = repo.refs[self.ref]
        except KeyError:
            self.tree = Tree()
            self.parents = []
            self.is_initialized = False
        else:
            self.tree = repo.tree(repo.commit(previous_commit_id).tree)
            self.parents = [previous_commit_id]
            self.is_initialized = True
        self.objects = {}
        self.messages = []

    @property
    def has_changes(self):
        return bool(self.objects)

    def get_config_variable(self, section, name):
        c = self.repo.get_config_stack()
        try:
            return c.get(section, name).decode('utf-8')
        except KeyError:
            raise GitError(
                '{0}.{1} not found in git config'.format(section, name))

    @property
    def author(self):
        name = self.get_config_variable('user', 'name')
        email = self.get_config_variable('user', 'email')
        return u'{0} <{1}>'.format(name, email)

    @property
    def timezone(self):
        if time.daylight and time.localtime().tm_isdst:
            return time.altzone
        return time.timezone

    def split_path(self, path):
        return path.lstrip('/').split('/')

    def __setitem__(self, key, value):
        path = self.split_path(key)
        filename = path.pop()
        directory = self.objects
        for name in path:
            if not name in directory:
                directory[name] = {}
            directory = directory[name]
        directory[filename] = Blob.from_string(value.encode('utf-8'))

    def _get_dir(self, path):
        directory = self.objects
        tree = self.tree
        for name in path:
            if tree:
                t = None
                if name in tree:
                    p, tid = tree[name]
                    if p & stat.S_IFDIR:
                        t = self.repo.tree(tid)
                tree = t
            if directory:
                directory = directory.get(name)
            if not tree and not directory:
                break
        return directory, tree

    def __getitem__(self, key):
        path = self.split_path(key)
        filename = path.pop()
        directory, tree = self._get_dir(path)
        blob = None
        if directory and filename in directory:
            blob = directory[filename]
        elif tree and filename in tree:
            p, bid = tree[filename]
            if p & stat.S_IFREG:
                blob = self.repo.get_blob(bid)
        if not blob:
            raise GitError('blob not found')
        return blob.data.decode('utf-8')

    def list_blobs(self, path):
        path = self.split_path(path)
        directory, tree = self._get_dir(path)
        names = []
        if tree:
            names += [entry.path for entry in tree.items()]
        if directory:
            names += directory.keys()
        return names

    def _store_objects(self, objects, tree):
        for name, obj in objects.iteritems():
            perm = stat.S_IFREG | 0644
            if isinstance(obj, Blob):
                self.repo.object_store.add_object(obj)
            else:
                perm = stat.S_IFDIR
                try:
                    p, tid = tree[name]
                except KeyError:
                    t = Tree()
                else:
                    if not p & stat.S_IFDIR:
                        raise GitError('{0} is not a directory'.format(name))
                    t = self.repo.tree(tid)
                self._store_objects(obj, t)
                obj = t
            tree.add(name, perm, obj.id)
        self.repo.object_store.add_object(tree)

    def add_message(self, message):
        self.messages += [message]

    def commit(self, message=None):
        if not self.has_changes:
            raise GitError(
                'nothing changed; use rollback to abort the transaction')
        if not message:
            if not self.messages:
                raise GitError('no message for commit')
            message = '\n'.join(self.messages)
        elif self.messages:
            message += u'\n\n' + u'\n'.join(self.messages)

        self._store_objects(self.objects, self.tree)

        commit = Commit()
        commit.tree = self.tree.id
        commit.parents = self.parents
        commit.author = commit.committer = self.author.encode('utf-8')
        commit.author_time = commit.commit_time = int(time.time())
        commit.author_timezone = commit.commit_timezone = -self.timezone
        commit.encoding = 'UTF-8'
        commit.message = message.encode('utf-8')
        self.repo.object_store.add_object(commit)
        self.repo.refs[self.ref] = commit.id

    def rollback(self):
        self.objects = {}
        self.messages = []


class auto_transaction(object):
    def __call__(self, fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return _inner

    def __enter__(self):
        global transaction
        self.active = not transaction
        if self.active:
            transaction = Transaction()
        return transaction

    def __exit__(self, type, value, traceback):
        global transaction
        if self.active:
            if type:
                transaction.rollback()
            elif transaction.has_changes:
                transaction.commit()
            transaction = None


@auto_transaction()
def init_repo():
    transaction = get_transaction(initialized=False)
    transaction['/VERSION'] = u'{0}\n'.format(get_version())
    transaction.add_message(u'Initialize Repository')
    transaction.is_initialized = True
