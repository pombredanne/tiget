from tiget.models.base import Model
from tiget.models.fields import TextField, ForeignKey
from tiget.models.user import User
from tiget.models.milestone import Milestone


def get_current_user():
    try:
        return User.current()
    except User.DoesNotExist:
        return None


class Ticket(Model):
    summary = TextField()
    description = TextField(null=True)
    milestone = ForeignKey(Milestone, null=True)
    reporter = ForeignKey(User, default=get_current_user)
    owner = ForeignKey(User, null=True)
