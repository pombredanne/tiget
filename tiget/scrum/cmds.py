from functools import wraps

from tiget.cmds import Cmd
from tiget.git import transaction
from tiget.table import Table
from tiget.scrum.models import Ticket, User
from tiget.utils import open_in_editor


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
            'id', 'summary', 'milestone', 'sprint', 'status', 'type'))
        self.print(table.render())


class CreateTicket(Cmd):
    names = Ticket.TYPE_CHOICES

    @property
    def description(self):
        return 'create ticket of type {}'.format(self.name)

    def run(self, *argv):
        try:
            ticket = Ticket(type=self.name)
            s = open_in_editor(ticket.dumps())
            ticket.loads(s)
            ticket.save()
        except Ticket.InvalidObject as e:
            raise self.error(e)


class SetTicketStatus(Cmd):
    names = [status for status in Ticket.STATUS_CHOICES if not status == 'new']

    @property
    def description(self):
        return 'set ticket status to {}'.format(self.name)

    def setup(self):
        self.parser.add_argument('ticket_id')

    @transaction.wrap()
    def do(self, args):
        ticket = Ticket.objects.get(id__startswith=args.ticket_id)
        ticket.status = self.name
        ticket.save()
