from tiget.conf import settings
from tiget.git import models


class User(models.Model):
    email = models.TextField(primary_key=True)
    name = models.TextField(null=True)

    @classmethod
    def current(cls):
        email = settings.scrum.current_user
        try:
            user = cls.objects.get(email=email)
        except User.DoesNotExist:
            raise User.DoesNotExist('user "{}" not found'.format(email))
        return user


class Sprint(models.Model):
    name = models.TextField(primary_key=True)
    description = models.TextField(null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    @classmethod
    def current(cls):
        name = settings.scrum.current_sprint
        return cls.objects.get(name=name) if name else None


def get_current_user():
    try:
        return User.current()
    except User.DoesNotExist:
        return None


def get_current_sprint():
    try:
        return Sprint.current()
    except Sprint.DoesNotExist:
        return None


class Ticket(models.Model):
    STATUS_CHOICES = (
        'new',
        'testing',
        'fixed',
        'invalid',
        'wontfix',
        'duplicate',
        'wtf',
    )
    TYPE_CHOICES = (
        'bug',
        'feature',
        'idea',
        'training',
        'story',
        'requirement',
        'wording',
    )
    summary = models.TextField()
    description = models.TextField(null=True)
    sprint = models.ForeignKey(Sprint, null=True, default=get_current_sprint)
    reporter = models.ForeignKey(User, default=get_current_user)
    owner = models.ForeignKey(User, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='new')
    type = models.TextField(choices=TYPE_CHOICES, default='bug')


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(User)
    text = models.TextField()
