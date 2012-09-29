from tiget.cmds import Cmd
from tiget.git import auto_transaction
from tiget.models import get_model

from tiget.simple_workflow.models import Ticket, User


class AcceptCmd(Cmd):
    """
    usage: accept TICKET_ID
    """
    help_text = 'accept ticket'

    @auto_transaction()
    def do(self, opts, ticket_id):
        try:
            ticket = Ticket.get(id=ticket_id)
            ticket.owner = User.current()
        except (Ticket.DoesNotExist, User.DoesNotExist) as e:
            raise self.error(e)
        ticket.save()
