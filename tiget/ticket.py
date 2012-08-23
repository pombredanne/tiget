from tiget.model import Model, TextField
from tiget.utils import open_in_editor

class Ticket(Model):
    summary = TextField()
    description = TextField()

    def open_in_editor(self):
        s = open_in_editor(self.serialize())
        self.deserialize(s)
