import stat
import time
import os
from functools import wraps
from collections import namedtuple
from pkg_resources import Requirement, resource_listdir, resource_string

import pygit2

import tiget
from tiget.settings import settings

_transaction = None


class GitError(Exception):
    pass


def get_transaction(initialized=True):
    if initialized and not _transaction.is_initialized:
        raise GitError('repository is not initialized; use tiget-setup-repository')
    elif not initialized and _transaction.is_initialized:
        raise GitError('repository is initialized')
    return _transaction


MemoryTree = namedtuple('MemoryTree', ['tree', 'childs', 'blobs'])

class Transaction(object):
    def __init__(self):
        try:
            repo = pygit2.Repository(settings.core.repository_path)
        except KeyError:
            raise GitError('no git repository found')
        self.repo = repo
        self.ref = 'refs/heads/{}'.format(settings.core.branchname)
        try:
            previous_commit_id = repo.lookup_reference(self.ref).oid
        except KeyError:
            tree = []
            self.parents = []
            self.is_initialized = False
        else:
            tree = repo[previous_commit_id].tree
            self.parents = [previous_commit_id]
            self.is_initialized = True
        self.has_changes = False
        self.memory_tree = MemoryTree(tree, {}, {})
        self.messages = []

    def config(self, name):
        return self.repo.config[name]

    def split_path(self, path):
        return path.lstrip('/').split('/')

    def get_memory_tree(self, path):
        memory_tree = self.memory_tree
        for name in path:
            if not name in memory_tree.childs:
                tree = []
                if name in memory_tree.tree:
                    entry = memory_tree.tree[name]
                    if entry.attributes & stat.S_IFDIR:
                        tree = entry.to_object()
                memory_tree.childs[name] = MemoryTree(tree, {}, {})
            memory_tree = memory_tree.childs[name]
        return memory_tree

    def exists(self, path):
        path = self.split_path(path)
        filename = path.pop()
        memory_tree = self.get_memory_tree(path)
        for files in (memory_tree.blobs, memory_tree.childs, memory_tree.tree):
            if filename in files:
                return True
        return False

    def get_blob(self, key):
        path = self.split_path(key)
        filename = path.pop()
        memory_tree = self.get_memory_tree(path)
        blob = None
        if filename in memory_tree.blobs:
            blob = memory_tree.blobs[filename]
        elif filename in memory_tree.tree:
            entry = memory_tree.tree[filename]
            if entry.attributes & stat.S_IFREG:
                blob = entry.to_object().data
        if not blob:
            raise GitError('blob not found')
        return blob

    def set_blob(self, key, value):
        path = self.split_path(key)
        filename = path.pop()
        memory_tree = self.get_memory_tree(path)
        memory_tree.blobs[filename] = value
        self.has_changes = True

    def list_blobs(self, path):
        path = self.split_path(path)
        memory_tree = self.get_memory_tree(path)
        names = set(memory_tree.blobs.iterkeys())
        for entry in memory_tree.tree:
            if entry.attributes & stat.S_IFREG:
                names.add(entry.name)
        return names

    def add_message(self, message):
        self.messages += [message]

    def _store_objects(self, memory_tree):
        treebuilder = self.repo.TreeBuilder()
        for entry in memory_tree.tree:
            treebuilder.insert(entry.name, entry.oid, entry.attributes)
        for name, content in memory_tree.blobs.iteritems():
            blob_id = self.repo.create_blob(content)
            treebuilder.insert(name, blob_id, stat.S_IFREG | 0644)
        for name, child in memory_tree.childs.iteritems():
            if not child.childs and not child.blobs:
                continue
            tree_id = self._store_objects(child)
            treebuilder.insert(name, tree_id, stat.S_IFDIR)
        return treebuilder.write()

    @property
    def author(self):
        try:
            name = self.config('user.name')
            email = self.config('user.email')
        except KeyError as e:
            raise GitError('{} not found in git config'.format(e))
        return pygit2.Signature(name, email)

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

        tree_id = self._store_objects(self.memory_tree)

        author = committer = self.author
        self.repo.create_commit(
            self.ref, author, committer, message, tree_id, self.parents, 'utf-8')

    def rollback(self):
        self.memory_tree = {}
        self.messages = []


def begin():
    global _transaction
    if _transaction:
        raise GitError('there is already a transaction running')
    _transaction = Transaction()


def commit(message=None):
    global _transaction
    if not _transaction:
        raise GitError('no transaction in progress')
    _transaction.commit(message)
    _transaction = None


def rollback():
    global _transaction
    if not _transaction:
        raise GitError('no transaction in progress')
    _transaction.rollback()
    _transaction = None


class auto_transaction(object):
    def __call__(self, fn):
        @wraps(fn)
        def _inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return _inner

    def __enter__(self):
        self.active = not _transaction
        if self.active:
            begin()
        return _transaction

    def __exit__(self, type, value, traceback):
        if self.active:
            if not type and _transaction.has_changes:
                commit()
            else:
                rollback()


def find_repository_path(cwd='.'):
    try:
        return pygit2.discover_repository(cwd)
    except KeyError:
        raise GitError('no git repository found')


@auto_transaction()
def init_repo():
    transaction = get_transaction(initialized=False)

    version_string = u'{}\n'.format(tiget.__version__)
    transaction.set_blob('/config/VERSION', version_string.encode('utf-8'))

    req = Requirement.parse('tiget')
    for filename in resource_listdir(req, 'tiget/config'):
        content = resource_string(req, 'tiget/config/{}'.format(filename))
        transaction.set_blob('/config/{}'.format(filename), content)

    transaction.add_message(u'Initialize Repository')
    transaction.is_initialized = True
