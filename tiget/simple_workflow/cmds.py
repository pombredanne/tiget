from tiget.cmds import cmd, CmdError
from tiget.git import auto_transaction
from tiget.models import get_model

from tiget.simple_workflow.models import Ticket, User


@cmd()
@auto_transaction()
def accept_cmd(opts, ticket_id):
    """
    accept ticket

    SYNOPSIS
        accept TICKET_ID
    """
    try:
        ticket = Ticket.get(id=ticket_id)
        ticket.owner = User.current()
    except (Ticket.DoesNotExist, User.DoesNotExist) as e:
        raise CmdError(e)
    ticket.save()
