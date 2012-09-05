from tiget.models.base import Model
from tiget.models.fields import TextField


class User(Model):
    email = TextField()
    name = TextField(null=True)
