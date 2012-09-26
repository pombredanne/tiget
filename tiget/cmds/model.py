from tiget.cmds.base import Cmd
from tiget.git import init_repo, GitError, auto_transaction
from tiget.models import get_model
from tiget.utils import open_in_editor


class CreateCmd(Cmd):
    """
    usage: create MODEL

    Create a new instance of MODEL.
    """
    name = 'create'
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


class InitCmd(Cmd):
    """
    usage: init

    Initializes the git repository for usage with tiget.
    """
    name = 'init'
    help_text = 'initialize the repository'

    def do(self, opts):
        try:
            init_repo()
        except GitError as e:
            raise self.error(e)


class EditCmd(Cmd):
    """
    usage: edit MODEL PK

    Edit MODEL instance with primary key PK.
    """
    name = 'edit'
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
