from tiget.cmds.base import Cmd
from tiget.git import auto_transaction
from tiget.table import Table


class ListCmd(Cmd):
    """
    usage: list
    """
    name = 'list'
    help_text = 'list tickets'
    aliases = ('ls',)

    @auto_transaction()
    def do(self, opts):
        from config.models import Ticket        # FIXME
        table = Table(u'id', u'summary', u'owner')
        for ticket in Ticket.all():
            table.add_row(
                ticket.id.hex,
                ticket.summary,
                ticket.owner.email if ticket.owner else u''
            )
        print table.render()
