import stat
from functools import wraps
from collections import namedtuple

import pygit2

from tiget.conf import settings
from tiget.git import GitError
from tiget.git.quote import quote_filename, unquote_filename


MemoryTree = namedtuple('MemoryTree', ['tree', 'childs', 'blobs'])


class Transaction(object):
    def __init__(self):
        repo = settings.core.repository
        if repo is None:
            raise GitError('core.repository is not set')
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
        path = list(map(quote_filename, path))
        filename = path.pop()
        memory_tree = self.get_memory_tree(path)
        for files in (memory_tree.blobs, memory_tree.childs, memory_tree.tree):
            if filename in files:
                return True
        return False

    def get_blob(self, path):
        *path, filename = map(quote_filename, path)
        memory_tree = self.get_memory_tree(path)
        content = None
        if filename in memory_tree.blobs:
            content = memory_tree.blobs[filename]
        elif filename in memory_tree.tree:
            entry = memory_tree.tree[filename]
            if entry.attributes & stat.S_IFREG:
                content = entry.to_object().data
        if content is None:
            raise GitError('blob not found')
        return content

    def set_blob(self, path, content):
        *path, filename = map(quote_filename, path)
        memory_tree = self.get_memory_tree(path)
        memory_tree.blobs[filename] = content
        self.has_changes = True

    def list_blobs(self, path):
        path = map(quote_filename, path)
        memory_tree = self.get_memory_tree(path)
        names = set(memory_tree.blobs.keys())
        for entry in memory_tree.tree:
            if entry.attributes & stat.S_IFREG:
                names.add(unquote_filename(entry.name))
        return names

    def add_message(self, message):
        self.messages += [message]

    def _store_objects(self, memory_tree):
        treebuilder = self.repo.TreeBuilder()
        for entry in memory_tree.tree:
            treebuilder.insert(entry.name, entry.oid, entry.attributes)
        for name, content in memory_tree.blobs.items():
            blob_id = self.repo.create_blob(content)
            treebuilder.insert(name, blob_id, stat.S_IFREG | 0o644)
        for name, child in memory_tree.childs.items():
            if not child.childs and not child.blobs:
                continue
            tree_id = self._store_objects(child)
            treebuilder.insert(name, tree_id, stat.S_IFDIR)
        return treebuilder.write()

    def commit(self, message=None):
        if not self.has_changes:
            raise GitError(
                'nothing changed; use rollback to abort the transaction')
        if not message:
            if not self.messages:
                raise GitError('no message for commit')
            message = '\n'.join(self.messages)
        elif self.messages:
            message += '\n\n' + '\n'.join(self.messages)

        tree_id = self._store_objects(self.memory_tree)

        try:
            name = self.repo.config['user.name']
            email = self.repo.config['user.email']
        except KeyError as e:
            raise GitError('{} not found in git config'.format(e))
        author = committer = pygit2.Signature(name, email)
        self.repo.create_commit(
            self.ref, author, committer, message, tree_id, self.parents, 'utf-8')

    def rollback(self):
        self.memory_tree = {}
        self.messages = []


_transaction = None

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


def current(initialized=True):
    if _transaction is None:
        raise GitError('no transaction running')
    elif initialized and not _transaction.is_initialized:
        raise GitError('repository is not initialized; use tiget-setup-repository')
    elif not initialized and _transaction.is_initialized:
        raise GitError('repository is initialized')
    return _transaction


class wrap(object):
    def __init__(self, message=None):
        self.message = message

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
                commit(self.message)
            else:
                rollback()
