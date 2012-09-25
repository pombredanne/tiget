from tiget.cmds.base import Cmd
from tiget.git import init_repo, GitError, auto_transaction, get_transaction
from tiget.models import Ticket, User
from tiget.table import Table


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
            ticket = Ticket.get(id=ticket_id)
        except Ticket.DoesNotExist as e:
            raise self.error(e)
        ticket.open_in_editor()
        ticket.save()


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


class ListCmd(Cmd):
    """
    usage: list
    """
    name = 'list'
    help_text = 'list tickets'
    aliases = ('ls',)

    @Cmd.argcount(0)
    @auto_transaction()
    def do(self, opts, args):
        table = Table(u'id', u'summary', u'owner')
        for ticket in Ticket.all():
            table.add_row(
                ticket.id.hex,
                ticket.summary,
                ticket.owner.email if ticket.owner else u''
            )
        print table.render()


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
            try:
                ticket.owner = User.current()
            except User.DoesNotExist:
                email = get_transaction().get_config_variable('user', 'email')
                raise self.error('no user found for {}'.format(email))
            ticket.open_in_editor()
            ticket.save()
        except GitError as e:
            raise self.error(e)
