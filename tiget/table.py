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

    def add_row(self, *args):
        # FIXME: check number of arguments
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
        available_width = (
            get_termsize().cols -
            (len(self.col_width) - 1) * 3 - 4)
        ratio = min(1, available_width / unscaled)
        widths = [max(1, math.floor(w * ratio)) for w in self.col_width]

        def _render_row(row, header=False):
            cells = []
            for value, width in zip(row, widths):
                cells += [wrap(value, width)]
            lines = []
            while any(cells):
                values = []
                for cell, width, style in zip(cells, widths, self.styles):
                    if header:
                        style = CENTER
                    value = style(cell.pop(0) if cell else '', width)
                    values += [value]
                lines += ['| ' + ' | '.join(values) + ' |']
            return '\n'.join(lines) + '\n'

        separator = '+-' + '-+-'.join('-' * w for w in widths) + '-+\n'

        s = separator
        s += _render_row(self.columns, header=True)
        s += separator
        for row in self.rows:
            s += _render_row(row)
        s += separator
        return s
