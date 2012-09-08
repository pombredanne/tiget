from tiget.models.base import Model
from tiget.models.fields import TextField

class Milestone(Model):
    name = TextField()
    description = TextField(null=True)
