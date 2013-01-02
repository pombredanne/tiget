from tiget.cmds import cmd, CmdError
from tiget.git import transaction
from tiget.git.models import get_model
from tiget.utils import paginate
from tiget.table import Table
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


@cmd(options='a')
@transaction.wrap()
def mine_cmd(opts):
    """
    list tickets owned by the current user

    SYNOPSIS
        mine [-a]
    """
    show_all = False
    for opt, arg in opts:
        if opt == '-a':
            show_all = True
    tickets = Ticket.objects.filter(owner=User.current())
    if not show_all:
        tickets = tickets.filter(status__in=('new', 'wtf'))
    field_names = ('id', 'summary', 'milestone', 'sprint', 'status', 'ticket_type')
    fields = [Ticket._meta.get_field(f) for f in field_names]
    table = Table(*(f.name for f in fields))
    for ticket in tickets:
        values = [f.dumps(getattr(ticket, f.attname)) for f in fields]
        table.add_row(*values)
    paginate(table.render())
