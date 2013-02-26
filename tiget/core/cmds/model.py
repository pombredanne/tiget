from tiget.cmds import Cmd
from tiget.cmds.types import model_type, dict_type
from tiget.git import transaction
from tiget.utils import open_in_editor
from tiget.table import Table
from tiget.plugins import plugins


__all__ = ['Create', 'Edit', 'Update', 'List', 'Stats']


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


class Update(Cmd):
    description = 'update model instance'

    def setup(self):
        self.parser.add_argument('model', type=model_type)
        self.parser.add_argument('pk')
        self.parser.add_argument('args', nargs='+', type=dict_type)

    @transaction.wrap()
    def do(self, args):
        try:
            instance = args.model.objects.get(pk__startswith=args.pk)
        except (args.model.DoesNotExist, args.model.MultipleObjectsReturned) as e:
            raise self.error(e)

        data = dict(ars.args)
        try:
            instance.load_data(data)
            instance.save()
        except args.model.InvalidObject as e:
            raise self.error(e)


class List(Cmd):
    description = 'list records'

    def setup(self):
        self.parser.add_argument('-f', '--fields')
        self.parser.add_argument('-o', '--order', default='pk')
        self.parser.add_argument('-s', '--slice', type=self.parse_slice)
        self.parser.add_argument('model', type=model_type)

    def parse_slice(self, value):
        parts = [int(part) if part else None for part in value.split(':')]
        return slice(*parts)

    @transaction.wrap()
    def do(self, args):
        objs = args.model.objects.order_by(*args.order.split(','))
        if args.slice:
            objs = objs[args.slice]
        fields = args.fields.split(',') if args.fields else None
        table = Table.from_queryset(objs, fields=fields)
        self.print(table.render())


class Stats(Cmd):
    description = 'display statistics for models'

    def do(self, args):
        table = Table('model', 'plugin', 'count')
        for plugin in plugins.values():
            for name, model in plugin.models.items():
                table.add_row(name, plugin.name, model.objects.count())
        self.print(table.render())
