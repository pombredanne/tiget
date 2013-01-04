from functools import wraps
from collections import OrderedDict

from tiget.cmds import Cmd
from tiget.git import transaction
from tiget.git.models import get_model
from tiget.utils import open_in_editor, paginate
from tiget.table import Table


__all__ = ['Create', 'Edit', 'List']


def model_type(model_name):
    try:
        model = get_model(model_name)
    except KeyError:
        raise TypeError
    return model


class Create(Cmd):
    description = 'create new model instance'

    def setup(self):
        self.parser.add_argument('model', type=model_type)

    @transaction.wrap()
    def do(self, args):
        try:
            instance = args.model()
            s = open_in_editor(instance.dumps())
            instance.loads(s)
            instance.save()
        except args.model.InvalidObject as e:
            raise self.error(e)


class Edit(Cmd):
    description = 'edit model instance'

    def setup(self):
        self.parser.add_argument('model', type=model_type)
        self.parser.add_argument('pk')

    @transaction.wrap()
    def do(self, args):
        try:
            instance = args.model.objects.get(pk__startswith=args.pk)
        except (args.model.DoesNotExist, args.model.MultipleObjectsReturned) as e:
            raise self.error(e)
        try:
            s = open_in_editor(instance.dumps())
            instance.loads(s)
            instance.save()
        except args.model.InvalidObject as e:
            raise self.error(e)


class List(Cmd):
    description = 'list records'

    def setup(self):
        self.parser.add_argument('-f', '--fields')
        self.parser.add_argument('-s', '--sort')
        self.parser.add_argument('-l', '--limit', type=int)
        self.parser.add_argument('model', type=model_type)

    @transaction.wrap()
    def do(self, args):
        fields = args.model._meta.writable_fields
        if args.fields:
            fields = [args.model._meta.get_field(f) for f in args.fields.split(',')]
        if args.sort:
            args.sort = args.sort.split(',')
            for field in args.sort:
                if field.startswith('-'):
                    field = field[1:]
                try:
                    args.model._meta.get_field(field)
                except KeyError as e:
                    raise self.error(e)
        table = Table(*(f.name for f in fields))
        objs = args.model.objects.all()
        if args.sort:
            objs = objs.order_by(*args.sort)
        if not args.limit is None:
            objs = objs[:args.limit]
        for instance in objs:
            values = [f.dumps(getattr(instance, f.attname)) for f in fields]
            table.add_row(*values)
        paginate(table.render())
