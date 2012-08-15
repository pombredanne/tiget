from tiget import settings
from tiget.cmd_registry import cmd_registry, Cmd
from tiget.git import GitError, GitTransaction

@cmd_registry.add
class BeginCmd(Cmd):
    """
    usage: begin
    """
    name = 'begin'
    help_text = 'begin transaction'

    @Cmd.argcount(0)
    def do(self, opts, args):
        if settings.transaction:
            raise self.error('there is already a transaction running')
        settings.transaction = GitTransaction()

@cmd_registry.add
class CommitCmd(Cmd):
    """
    usage: commit [MESSAGE]
    """
    name = 'commit'
    help_text = 'commit transaction'

    @Cmd.argcount(0, 1)
    def do(self, opts, args):
        if not settings.transaction:
            raise self.error('no transaction running')
        message = None
        if args:
            message = args[0]
        try:
            settings.transaction.commit(message)
        except GitError as e:
            raise self.error(e)
        settings.transaction = None

@cmd_registry.add
class RollbackCmd(Cmd):
    """
    usage: rollback
    """
    name = 'rollback'
    help_text = 'roll back transaction'

    @Cmd.argcount(0)
    def do (self, opts, args):
        if not settings.transaction:
            raise self.error('no transaction running')
        settings.transaction.rollback()
        settings.transaction = None
