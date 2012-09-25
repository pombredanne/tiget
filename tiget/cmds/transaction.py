from tiget import git
from tiget.cmds.base import Cmd
from tiget.git import GitError


class BeginCmd(Cmd):
    """
    usage: begin
    """
    name = 'begin'
    help_text = 'begin transaction'

    def do(self, opts):
        if git.transaction:
            raise self.error('there is already a transaction running')
        git.transaction = git.Transaction()


class CommitCmd(Cmd):
    """
    usage: commit [MESSAGE]
    """
    name = 'commit'
    help_text = 'commit transaction'

    def do(self, opts, message=None):
        if not git.transaction:
            raise self.error('no transaction running')
        try:
            git.transaction.commit(message)
        except GitError as e:
            raise self.error(e)
        git.transaction = None


class RollbackCmd(Cmd):
    """
    usage: rollback
    """
    name = 'rollback'
    help_text = 'roll back transaction'

    def do(self, opts):
        if not git.transaction:
            raise self.error('no transaction running')
        git.transaction.rollback()
        git.transaction = None
