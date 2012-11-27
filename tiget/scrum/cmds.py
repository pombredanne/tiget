from tiget.cmds import cmd, CmdError
from tiget.git import transaction
from tiget.git.models import get_model

from tiget.scrum.models import Ticket, User


@cmd()
@transaction.wrap()
def accept_cmd(opts, ticket_id):
    """
    accept ticket

    SYNOPSIS
        accept TICKET_ID
    """
    try:
        ticket = Ticket.objects.get(id__startswith=ticket_id)
        ticket.owner = User.current()
    except (Ticket.DoesNotExist, User.DoesNotExist) as e:
        raise CmdError(e)
    ticket.save()
