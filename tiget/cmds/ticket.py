from tiget.cmds.base import Cmd
from tiget.git import init_repo, GitError, auto_transaction
from tiget.models import Ticket, User
from tiget.table import Table


class AcceptCmd(Cmd):
    """
    usage: accept TICKET_ID
    """
    name = 'accept'
    help_text = 'accept ticket'

    @auto_transaction()
    def do(self, opts, ticket_id):
        try:
            ticket = Ticket.get(id=ticket_id)
            ticket.owner = User.current()
        except (Ticket.DoesNotExist, User.DoesNotExist) as e:
            raise self.error(e)
        ticket.save()


class ListCmd(Cmd):
    """
    usage: list
    """
    name = 'list'
    help_text = 'list tickets'
    aliases = ('ls',)

    @auto_transaction()
    def do(self, opts):
        table = Table(u'id', u'summary', u'owner')
        for ticket in Ticket.all():
            table.add_row(
                ticket.id.hex,
                ticket.summary,
                ticket.owner.email if ticket.owner else u''
            )
        print table.render()
