from functools import wraps

from tiget.cmds import Cmd
from tiget.git import transaction, GitError
from tiget.git.sync import fetch, push, merge


__all__ = ['Begin', 'Commit', 'Rollback', 'Fetch', 'Push', 'Merge']


def catch_git_error(fn):
    @wraps(fn)
    def _inner(self, args):
        try:
            return fn(self, args)
        except GitError as e:
            raise self.error(e)
    return _inner


class Begin(Cmd):
    description = 'begin transaction'

    @catch_git_error
    def do(self, args):
        transaction.begin()


class Commit(Cmd):
    description = 'commit transaction'

    def setup(self):
        self.parser.add_argument('message', nargs='?')

    @catch_git_error
    def do(self, args):
        transaction.commit(args.message)


class Rollback(Cmd):
    description = 'roll back transaction'

    @catch_git_error
    def do(self, args):
        transaction.rollback()


class Fetch(Cmd):
    description = 'fetch changes from remote repository'

    @catch_git_error
    def do(self, args):
        fetch()


class Push(Cmd):
    description = 'push changes to remote repository'

    @catch_git_error
    def do(self, args):
        push()


class Merge(Cmd):
    description = 'merge remote and local changes'

    @catch_git_error
    def do(self, args):
        merge()
