import os, stat, time
from collections import defaultdict
from functools import wraps
from dulwich.objects import Blob, Tree, Commit
from dulwich.repo import Repo, NotGitRepository
from tiget import settings, get_version

transaction = None

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
            repo = Repo(os.getcwd())
        except NotGitRepository:
            raise GitError('no git repository found')
        self.repo = repo
        self.ref = 'refs/heads/{0}'.format(settings.branchname)
        try:
            previous_commit_id = repo.refs[self.ref]
        except KeyError:
            self.tree = Tree()
            self.parents = []
        else:
            self.tree = repo.tree(repo.commit(previous_commit_id).tree)
            self.parents = [previous_commit_id]
        self.objects = defaultdict(lambda: defaultdict())
        self.messages = []

    @property
    def is_initialized(self):
        return self.ref in self.repo.refs

    @property
    def has_changes(self):
        return bool(self.objects)

    def get_config_variable(self, section, name):
        c = self.repo.get_config_stack()
        try:
            return c.get(section, name).decode('utf-8')
        except KeyError:
            raise GitError('{0}.{1} not found in git config'.format(section, name))

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

    def get_dir(self, path):
        directory = self.objects
        for name in path:
            directory = directory[name]
        return directory

    def add_blob(self, path, content):
        path = self.split_path(path)
        filename = path.pop()
        directory = self.get_dir(path)
        directory[filename] = Blob.from_string(content.encode('utf-8'))

    def get_file(self, path):
        path = self.split_path(path)
        filename = path.pop()
        directory = self.get_dir(path)
        return directory[filename]

    def list_files(self, path):
        path = self.split_path(path)
        directory = self.get_dir(path)
        return directory

    def _add_objects(self, objects, tree):
        for name, obj in objects.iteritems():
            perm = stat.S_IFREG | 0644
            if not isinstance(obj, Blob):
                perm = stat.S_IFDIR
                try:
                    p, tid = tree[name]
                except KeyError:
                    t = Tree()
                else:
                    if not p & stat.S_IFDIR:
                        raise GitError('{0} is not a directory'.format(name))
                    t = self.repo.tree(tid)
                self._add_objects(obj, t)
                obj = t
            self.repo.object_store.add_object(obj)
            tree.add(name, perm, obj.id)

    def add_message(self, message):
        self.messages += [message]

    def commit(self, message=None):
        if not self.has_changes:
            raise GitError('nothing changed; use rollback to abort the transaction')
        if not message:
            if not self.messages:
                raise GitError('no message for commit')
            message = '\n'.join(self.messages)
        elif self.messages:
            message += u'\n\n' + u'\n'.join(self.messages)

        self._add_objects(self.objects, self.tree)
        self.repo.object_store.add_object(self.tree)

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
        self.objects = defaultdict(lambda: defaultdict())
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
    transaction.add_blob('/VERSION', u'{0}\n'.format(get_version()))
    transaction.add_blob('/tickets/.keep', u'')
    transaction.add_message(u'Initialize Repository')
