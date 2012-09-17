from tiget.models.base import Model
from tiget.models.fields import TextField

class Milestone(Model):
    name = TextField(primary_key=True)
    description = TextField(null=True)
