from tiget.git import models, get_config


class User(models.Model):
    email = models.TextField(primary_key=True)
    name = models.TextField(null=True)

    @classmethod
    def current(cls, **kwargs):
        return cls.objects.get(email=get_config('user.email'))


class Milestone(models.Model):
    name = models.TextField(primary_key=True)
    description = models.TextField(null=True)
    due = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)


class Sprint(models.Model):
    name = models.TextField(primary_key=True)
    description = models.TextField(null=True)
    milestone = models.ForeignKey(Milestone, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()


def get_current_user():
    try:
        return User.current()
    except User.DoesNotExist:
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
    milestone = models.ForeignKey(Milestone, null=True)
    sprint = models.ForeignKey(Sprint, null=True)
    reporter = models.ForeignKey(User, default=get_current_user)
    owner = models.ForeignKey(User, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='new')
    ticket_type = models.TextField(choices=TYPE_CHOICES, default='bug')
