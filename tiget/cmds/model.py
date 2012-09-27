from collections import OrderedDict
from functools import wraps

from tiget.cmds.base import Cmd
from tiget.git import GitError, auto_transaction
from tiget.models import get_model
from tiget.utils import open_in_editor
from tiget.table import Table


def with_model(fn):
    @wraps(fn)
    def _inner(self, opts, model_name, *args):
        try:
            model = get_model(model_name)
        except KeyError:
            raise self.error('model "{}" does not exist'.format(model_name))
        return fn(self, opts, model, *args)
    return _inner


class CreateCmd(Cmd):
    """
    usage: create MODEL

    Create a new instance of MODEL.
    """
    help_text = 'create new model instance'

    @auto_transaction()
    @with_model
    def do(self, opts, model):
        try:
            instance = model()
            s = open_in_editor(instance.dumps())
            instance.loads(s)
            instance.save()
        except model.InvalidObject as e:
            raise self.error(e)


class EditCmd(Cmd):
    """
    usage: edit MODEL PK

    Edit MODEL instance with primary key PK.
    """
    help_text = 'edit model instance'

    @auto_transaction()
    @with_model
    def do(self, opts, model, pk):
        try:
            instance = model.get(pk=pk)
        except model.DoesNotExist as e:
            raise self.error(e)
        try:
            s = open_in_editor(instance.dumps())
            instance.loads(s)
            instance.save()
        except model.InvalidObject as e:
            raise self.error(e)


class ListCmd(Cmd):
    """
    usage: list
    """
    help_text = 'list tickets'
    options = 'f:'

    @auto_transaction()
    @with_model
    def do(self, opts, model):
        fields = model._fields
        for opt, arg in opts:
            if opt == '-f':
                fields = OrderedDict()
                for fname in arg.split(','):
                    try:
                        fields[fname] = model._fields[fname]
                    except KeyError as e:
                        raise self.error(
                            'Field "{}" does not exist'.format(fname))
        table = Table(*fields.keys())
        for instance in model.all():
            values = [f.dumps(instance._data[k]) for k, f in fields.iteritems()]
            table.add_row(*values)
        print table.render()
