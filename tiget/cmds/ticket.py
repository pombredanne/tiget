from tiget.cmd_registry import cmd_registry, Cmd
from tiget.git import init_repo, GitError, auto_transaction
from tiget.ticket import Ticket
from tiget.table import Table


@cmd_registry.add
class EditCmd(Cmd):
    """
    usage: edit TICKET_ID

    Edit ticket with id TICKET_ID.
    """
    name = 'edit'
    help_text = 'edit ticket'

    @Cmd.argcount(1)
    @auto_transaction()
    def do(self, opts, args):
        ticket_id = args[0]
        try:
            ticket = Ticket.get(ticket_id)
        except Ticket.DoesNotExist() as e:
            raise self.error(e)
        ticket.open_in_editor()
        ticket.save()


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
        table = Table(u'id', u'summary')
        for ticket in Ticket.all():
            table.add_row(ticket.id.hex, ticket.summary)
        print table.render()


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
