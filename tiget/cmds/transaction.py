from tiget import git
from tiget.cmds.base import Cmd


class BeginCmd(Cmd):
    """
    usage: begin
    """
    help_text = 'begin transaction'

    def do(self, opts):
        if git.transaction:
            raise self.error('there is already a transaction running')
        git.transaction = git.Transaction()


class CommitCmd(Cmd):
    """
    usage: commit [MESSAGE]
    """
    help_text = 'commit transaction'

    def do(self, opts, message=None):
        if not git.transaction:
            raise self.error('no transaction running')
        try:
            git.transaction.commit(message)
        except git.GitError as e:
            raise self.error(e)
        git.transaction = None


class RollbackCmd(Cmd):
    """
    usage: rollback
    """
    help_text = 'roll back transaction'

    def do(self, opts):
        if not git.transaction:
            raise self.error('no transaction running')
        git.transaction.rollback()
        git.transaction = None
