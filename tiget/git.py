import os
import stat
import time
from functools import wraps
from collections import namedtuple

from dulwich.objects import Blob, Tree, Commit
from dulwich.repo import Repo, NotGitRepository

from tiget import get_version
from tiget.settings import settings

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


MemoryTree = namedtuple('MemoryTree', ['tree', 'childs', 'blobs'])

class Transaction(object):
    def __init__(self):
        try:
            repo = Repo(repository_path or os.getcwd())
        except NotGitRepository:
            raise GitError('no git repository found')
        self.repo = repo
        self.ref = 'refs/heads/{}'.format(settings.branchname)
        try:
            previous_commit_id = repo.refs[self.ref]
        except KeyError:
            tree = Tree()
            self.parents = []
            self.is_initialized = False
        else:
            tree = repo.tree(repo.commit(previous_commit_id).tree)
            self.parents = [previous_commit_id]
            self.is_initialized = True
        self.has_changes = False
        self.memory_tree = MemoryTree(tree, {}, {})
        self.messages = []

    def get_config_variable(self, section, name):
        c = self.repo.get_config_stack()
        try:
            return c.get(section, name).decode('utf-8')
        except KeyError:
            raise GitError(
                '{}.{} not found in git config'.format(section, name))

    @property
    def author(self):
        name = self.get_config_variable('user', 'name')
        email = self.get_config_variable('user', 'email')
        return u'{} <{}>'.format(name, email)

    @property
    def timezone(self):
        if time.daylight and time.localtime().tm_isdst:
            return time.altzone
        return time.timezone

    def split_path(self, path):
        return path.lstrip('/').split('/')

    def get_memory_tree(self, path):
        memory_tree = self.memory_tree
        for name in path:
            if not name in memory_tree.childs:
                tree = Tree()
                if name in memory_tree.tree:
                    p, tid = memory_tree.tree[name]
                    if p & stat.S_IFDIR:
                        tree = self.repo.tree(tid)
                memory_tree.childs[name] = MemoryTree(tree, {}, {})
            memory_tree = memory_tree.childs[name]
        return memory_tree

    def get_blob(self, key):
        path = self.split_path(key)
        filename = path.pop()
        memory_tree = self.get_memory_tree(path)
        blob = None
        if filename in memory_tree.blobs:
            blob = memory_tree.blobs[filename]
        elif filename in memory_tree.tree:
            perm, blob_id = memory_tree.tree[filename]
            if perm & stat.S_IFREG:
                blob = self.repo.get_blob(blob_id)
        if not blob:
            raise GitError('blob not found')
        return blob.data

    def set_blob(self, key, value):
        path = self.split_path(key)
        filename = path.pop()
        memory_tree = self.get_memory_tree(path)
        memory_tree.blobs[filename] = Blob.from_string(value)
        self.has_changes = True

    def list_blobs(self, path):
        path = self.split_path(path)
        memory_tree = self.get_memory_tree(path)
        names = set()
        for entry in memory_tree.tree.items():
            if entry.mode & stat.S_IFREG:
                names.add(entry.path)
        names = set(entry.path for entry in memory_tree.tree.items())
        names.update(memory_tree.blobs.keys())
        return names

    def _store_objects(self, memory_tree):
        perm = stat.S_IFREG | 0644
        for name, blob in memory_tree.blobs.iteritems():
            self.repo.object_store.add_object(blob)
            memory_tree.tree.add(name, perm, blob.id)
        for name, child in memory_tree.childs.iteritems():
            if not child.childs and not child.blobs:
                continue
            self._store_objects(child)
            memory_tree.tree.add(name, stat.S_IFDIR, child.tree.id)
        self.repo.object_store.add_object(memory_tree.tree)

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

        self._store_objects(self.memory_tree)

        commit = Commit()
        commit.tree = self.memory_tree.tree.id
        commit.parents = self.parents
        commit.author = commit.committer = self.author.encode('utf-8')
        commit.author_time = commit.commit_time = int(time.time())
        commit.author_timezone = commit.commit_timezone = -self.timezone
        commit.encoding = 'UTF-8'
        commit.message = message.encode('utf-8')
        self.repo.object_store.add_object(commit)
        self.repo.refs[self.ref] = commit.id

    def rollback(self):
        self.memory_tree = {}
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
    version_string = u'{}\n'.format(get_version())
    transaction.set_blob('/VERSION', version_string.encode('utf-8'))
    transaction.add_message(u'Initialize Repository')
    transaction.is_initialized = True
