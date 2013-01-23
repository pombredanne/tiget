from tiget.git import transaction, init_repo, GitError
from tiget.cmds import Cmd


__all__ = ['Begin', 'Commit', 'Rollback', 'Setup']


class Begin(Cmd):
    description = 'begin transaction'

    def do(self, args):
        try:
            transaction.begin()
        except GitError as e:
            raise self.error(e)


class Commit(Cmd):
    description = 'commit transaction'

    def setup(self):
        self.parser.add_argument('message', nargs='?')

    def do(self, args):
        try:
            transaction.commit(args.message)
        except GitError as e:
            raise self.error(e)


class Rollback(Cmd):
    description = 'roll back transaction'

    def do(self, args):
        try:
            transaction.rollback()
        except GitError as e:
            raise self.error(e)


class Setup(Cmd):
    description = 'set up repository for use with tiget'

    def do(self, args):
        try:
            init_repo()
        except GitError as e:
            raise self.error(e)
