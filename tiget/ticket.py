from tiget.model import Model, TextField
from tiget.utils import edit_content

class Ticket(Model):
    fields = {
        'summary': TextField(),
        'description': TextField(),
    }

    def get_file_content(self):
        content = u''
        for name in ('summary', 'description'):
            field = self.fields[name]
            if field.hidden:
                continue
            value = self.data.get(name, field.default) or u''
            value = value.replace(u'\n', u'\n    ')
            content += u'{0}: {1}\n'.format(name, value)
        return content

    def edit(self):
        s = edit_content(self.serialize())
        self.deserialize(s)
        self.save()
