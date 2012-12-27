from functools import wraps
from collections import OrderedDict

from tiget.cmds import cmd, CmdError
from tiget.git import transaction
from tiget.git.models import get_model
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
@transaction.wrap()
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
@transaction.wrap()
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
        instance = model.objects.get(pk__startswith=pk)
    except (model.DoesNotExist, model.MultipleObjectsReturned) as e:
        raise CmdError(e)
    try:
        s = open_in_editor(instance.dumps())
        instance.loads(s)
        instance.save()
    except model.InvalidObject as e:
        raise CmdError(e)


@cmd(options='f:s:l:')
@transaction.wrap()
@with_model
def list_cmd(opts, model):
    """
    list records

    SYNOPSIS
        list [-f FIELDS] [-s SORT_ORDER] [-l LIMIT] MODEL
    """
    fields = model._meta.fields
    order_by = None
    limit = None
    for opt, arg in opts:
        if opt == '-f':
            try:
                fields = [model._meta.get_field(f) for f in arg.split(',')]
            except KeyError as e:
                raise CmdError(e)
        elif opt == '-s':
            order_by = arg.split(',')
            for field in order_by:
                if field.startswith('-'):
                    field = field[1:]
                try:
                    model._meta.get_field(field)
                except KeyError as e:
                    raise CmdError(e)
        elif opt == '-l':
            try:
                limit = int(arg)
            except ValueError as e:
                raise CmdError(e)
    table = Table(*(f.name for f in fields))
    objs = model.objects.all()
    if order_by:
        objs = objs.order_by(*order_by)
    if not limit is None:
        objs = objs[:limit]
    for instance in objs:
        values = [f.dumps(getattr(instance, f.attname)) for f in fields]
        table.add_row(*values)
    print(table.render())
