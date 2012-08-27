from tiget.cmd_registry import cmd_registry, Cmd
from tiget.git import init_repo, GitError, auto_transaction
from tiget.ticket import Ticket

@cmd_registry.add
class InitCmd(Cmd):
    """
    usage: init

    Initializes the git repository for usage with tiget.
    """
    name = 'init'
    help_text = 'initialize the repository'

    @Cmd.argcount(0)
    def do(self, opts, args):
        try:
            init_repo()
        except GitError as e:
            raise self.error(e)

@cmd_registry.add
class ListCmd(Cmd):
    """
    usage: list
    """
    name = 'list'
    help_text = 'list tickets'

    @Cmd.argcount(0)
    @auto_transaction()
    def do(self, opts, args):
        try:
            for ticket in Ticket.all():
                print '{0} | {1}'.format(ticket.id.hex, ticket.summary)
        except GitError as e:
            raise self.error(e)

@cmd_registry.add
class NewCmd(Cmd):
    """
    usage: new

    Create a new ticket.
    """
    name = 'new'
    help_text = 'create new ticket'

    @Cmd.argcount(0)
    @auto_transaction()
    def do(self, opts, args):
        try:
            ticket = Ticket()
            ticket.open_in_editor()
            ticket.save()
        except GitError as e:
            raise self.error(e)
