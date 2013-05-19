import math
from textwrap import wrap

from tiget.utils import get_termsize

CENTER = lambda x, width: x.center(width)
LJUST = lambda x, width: x.ljust(width)
RJUST = lambda x, width: x.rjust(width)


class Table:
    def __init__(self, *args):
        self.columns = args
        self.rows = []
        self.col_width = [len(col) for col in args]
        self.styles = [LJUST] * len(args)

    @classmethod
    def from_queryset(cls, queryset, fields=None):
        if fields is None:
            fields = queryset.model._meta.writable_fields
        else:
            fields = [queryset.model._meta.get_field(f) for f in fields]
        table = cls(*(f.name for f in fields))
        for instance in queryset:
            values = []
            for f in fields:
                try:
                    fn = getattr(instance, 'get_{}_display'.format(f.name))
                except AttributeError:
                    value = f.dumps(getattr(instance, f.attname))
                else:
                    value = fn()
                values.append(value)
            table.add_row(*values)
        return table

    def add_row(self, *args):
        column_count = len(self.columns)
        if not len(args) == column_count:
            raise TypeError(
                'expected exactly {} arguments'.format(column_count))
        args = [str(x or '') for x in args]
        self.rows.append(args)
        for i, col in enumerate(args):
            lines = col.splitlines()
            if lines:
                linelen = max(len(line) for line in lines)
            else:
                linelen = 0
            self.col_width[i] = max(linelen, self.col_width[i])

    def render(self):
        unscaled = sum(self.col_width)
        sep_width = (len(self.col_width) - 1) * 3
        available_width = get_termsize().cols - sep_width - 4
        ratio = min(1, available_width / unscaled)
        widths = [max(1, math.floor(w * ratio)) for w in self.col_width]

        def _render_row(row, header=False):
            cells = [wrap(value, width) for value, width in zip(row, widths)]
            lines = []
            while any(cells):
                values = []
                for cell, width, style in zip(cells, widths, self.styles):
                    if header:
                        style = CENTER
                    value = style(cell.pop(0) if cell else '', width)
                    values += [value]
                line = '| {} |'.format(' | '.join(values))
                lines.append(line)
            return '\n'.join(lines) + '\n'

        separator = '+-' + '-+-'.join('-' * w for w in widths) + '-+\n'

        s = separator
        s += _render_row(self.columns, header=True)
        s += separator
        for row in self.rows:
            s += _render_row(row)
        s += separator
        return s
