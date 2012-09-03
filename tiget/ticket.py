from tiget.model import Model, TextField
from tiget.utils import open_in_editor


class Ticket(Model):
    summary = TextField()
    description = TextField(null=True)

    def open_in_editor(self):
        s = open_in_editor(self.dumps())
        self.loads(s)
