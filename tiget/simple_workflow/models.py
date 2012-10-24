from tiget.models import Model, TextField, ForeignKey
from tiget.git import get_config


class User(Model):
    email = TextField(primary_key=True)
    name = TextField(null=True)

    @classmethod
    def current(cls, **kwargs):
        return cls.objects.get(email=get_config('user.email'))


class Milestone(Model):
    name = TextField(primary_key=True)
    description = TextField(null=True)


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
    status = TextField(choices=('new', 'testing', 'done'), default='new')
