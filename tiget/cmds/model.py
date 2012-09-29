from functools import wraps
from collections import OrderedDict

from tiget.cmds.base import cmd, CmdError
from tiget.git import auto_transaction
from tiget.models import get_model
from tiget.utils import open_in_editor
from tiget.table import Table


def with_model(fn):
    @wraps(fn)
    def _inner(opts, model_name, *args):
        try:
            model = get_model(model_name)
        except KeyError:
            raise CmdError('model "{}" does not exist'.format(model_name))
        return fn(opts, model, *args)
    return _inner


@cmd()
@auto_transaction()
@with_model
def create_cmd(opts, model):
    """
    create new model instance

    SYNOPSIS
        create MODEL

    DESCRIPTION
        Create a new instance of MODEL.
    """
    try:
        instance = model()
        s = open_in_editor(instance.dumps())
        instance.loads(s)
        instance.save()
    except model.InvalidObject as e:
        raise CmdError(e)


@cmd()
@auto_transaction()
@with_model
def edit_cmd(opts, model, pk):
    """
    edit model instance

    SYNOPSIS
        edit MODEL PK

    DESCRIPTION
        Edit MODEL instance with primary key PK.
    """
    try:
        instance = model.get(pk=pk)
    except model.DoesNotExist as e:
        raise CmdError(e)
    try:
        s = open_in_editor(instance.dumps())
        instance.loads(s)
        instance.save()
    except model.InvalidObject as e:
        raise CmdError(e)


@cmd(options='f:')
@auto_transaction()
@with_model
def list_cmd(opts, model):
    """
    list records

    SYNOPSIS
        list [-f FIELDS] MODEL
    """
    fields = model._fields
    for opt, arg in opts:
        if opt == '-f':
            fields = OrderedDict()
            for fname in arg.split(','):
                try:
                    fields[fname] = model._fields[fname]
                except KeyError as e:
                    raise CmdError( 'Field "{}" does not exist'.format(fname))
    table = Table(*fields.keys())
    for instance in model.all():
        values = [f.dumps(instance._data[k]) for k, f in fields.iteritems()]
        table.add_row(*values)
    print table.render()
