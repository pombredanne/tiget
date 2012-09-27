from tiget.cmds.base import Cmd
from tiget.git import GitError, auto_transaction
from tiget.models import get_model
from tiget.utils import open_in_editor


class CreateCmd(Cmd):
    """
    usage: create MODEL

    Create a new instance of MODEL.
    """
    help_text = 'create new model instance'
    aliases = ('new',)

    @auto_transaction()
    def do(self, opts, model_name):
        try:
            model = get_model(model_name)
        except KeyError:
            raise self.error('model "{}" does not exist'.format(model_name))
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
    def do(self, opts, model_name, pk):
        try:
            model = get_model(model_name)
        except KeyError:
            raise self.error('model "{}" does not exist'.format(model_name))
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
