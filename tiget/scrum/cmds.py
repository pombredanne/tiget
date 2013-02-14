from functools import wraps

from tiget.cmds import Cmd
from tiget.git import transaction
from tiget.table import Table
from tiget.scrum.models import Ticket, User


def require_user(fn):
    @wraps(fn)
    def _inner(self, args):
        try:
            user = User.current()
        except User.DoesNotExist as e:
            raise self.error(e)
        return fn(self, args, user)
    return _inner


class Accept(Cmd):
    description = 'accept ticket'

    def setup(self):
        self.parser.add_argument('ticket_id')

    @transaction.wrap()
    @require_user
    def do(self, args, user):
        try:
            ticket = Ticket.objects.get(id__startswith=args.ticket_id)
            ticket.owner = user
        except (Ticket.DoesNotExist, User.DoesNotExist) as e:
            raise self.error(e)
        ticket.save()


class Mine(Cmd):
    description = 'list tickets owned by the current user'

    def setup(self):
        self.parser.add_argument('-a', '--all', action='store_true')

    @transaction.wrap()
    @require_user
    def do(self, args, user):
        tickets = Ticket.objects.filter(owner=user)
        if not args.all:
            tickets = tickets.filter(status__in=('new', 'wtf'))
        table = Table.from_queryset(tickets, fields=(
            'id', 'summary', 'milestone', 'sprint', 'status', 'ticket_type'))
        self.print(table.render())
