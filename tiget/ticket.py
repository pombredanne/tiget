from tiget.model import Model, TextField
from tiget.utils import edit_content

class Ticket(Model):
    fields = {
        'summary': TextField(),
        'description': TextField(),
    }

    def edit(self):
        s = edit_content(self.serialize())
        self.deserialize(s)
        self.save()
