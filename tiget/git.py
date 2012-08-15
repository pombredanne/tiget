import os, stat, time
from collections import defaultdict
from contextlib import contextmanager
from dulwich.objects import Blob, Tree, Commit
from dulwich.config import StackedConfig
from dulwich.repo import Repo, NotGitRepository
from tiget import settings, get_version

class GitError(Exception):
    pass

def get_config_variable(section, name):
    c = StackedConfig(StackedConfig.default_backends())
    try:
        return c.get(section, name).decode('utf-8')
    except KeyError:
        raise GitError('{0}.{1} not found in git config'.format(section, name))

class GitTransaction(object):
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
        else:
            self.tree = repo.tree(repo.commit(previous_commit_id).tree)
        self.objects = defaultdict(lambda: defaultdict())
        self.messages = []

    @property
    def is_initialized(self):
        return self.ref in self.repo.refs

    @property
    def has_changes(self):
        return bool(self.objects)

    @property
    def author(self):
        name = get_config_variable('user', 'name')
        email = get_config_variable('user', 'email')
        return u'{0} <{1}>'.format(name, email)

    @property
    def timezone(self):
        if time.daylight and time.localtime().tm_isdst:
            return time.altzone
        return time.timezone

    def add_file(self, path, content):
        blob = Blob.from_string(content.encode('utf-8'))
        path = path.lstrip('/').split('/')
        filename = path.pop()
        directory = self.objects
        for name in path:
            directory = directory[name]
        directory[filename] = blob

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

@contextmanager
def need_transaction():
    transaction = settings.transaction
    if not transaction:
        transaction = GitTransaction()
    try:
        yield transaction
    except:
        if not settings.transaction:
            transaction.rollback()
        raise
    else:
        if not settings.transaction and transaction.has_changes:
            if transaction.has_changes:
                transaction.commit()

def init_repo():
    with need_transaction() as transaction:
        if transaction.is_initialized:
            raise GitError('already initialized')
        transaction.add_file('/VERSION', u'{0}\n'.format(get_version()))
        transaction.add_file('/tickets/.keep', u'')
        transaction.add_message(u'Initialize Repository')
