from tiget.models.base import Model
from tiget.models.fields import TextField
from tiget.git import auto_transaction, get_transaction


class User(Model):
    email = TextField(primary_key=True)
    name = TextField(null=True)

    @classmethod
    @auto_transaction()
    def current(cls, **kwargs):
        transaction = get_transaction()
        return cls.get(email=transaction.get_config_variable('user', 'email'))
