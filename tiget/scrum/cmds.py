from tiget.cmds import Cmd
from tiget.git import transaction
from tiget.utils import paginate
from tiget.table import Table
from tiget.scrum.models import Ticket, User


class Accept(Cmd):
    description = 'accept ticket'

    def setup(self):
        self.parser.add_argument('ticket_id')

    @transaction.wrap()
    def do(self, args):
        try:
            ticket = Ticket.objects.get(id__startswith=args.ticket_id)
            ticket.owner = User.current()
        except (Ticket.DoesNotExist, User.DoesNotExist) as e:
            raise self.error(e)
        ticket.save()


class Mine(Cmd):
    description = 'list tickets owned by the current user'

    def setup(self):
        self.parser.add_argument('-a', '--all', action='store_true')

    @transaction.wrap()
    def do(self, args):
        tickets = Ticket.objects.filter(owner=User.current())
        if not args.all:
            tickets = tickets.filter(status__in=('new', 'wtf'))
        field_names = ('id', 'summary', 'milestone', 'sprint', 'status', 'ticket_type')
        fields = [Ticket._meta.get_field(f) for f in field_names]
        table = Table(*(f.name for f in fields))
        for ticket in tickets:
            values = [f.dumps(getattr(ticket, f.attname)) for f in fields]
            table.add_row(*values)
        paginate(table.render())
