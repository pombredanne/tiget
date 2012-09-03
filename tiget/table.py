from collections import namedtuple

from tiget.utils import get_termsize

CENTER = lambda x, width: x.center(width)
LJUST = lambda x, width: x.ljust(width)
RJUST = lambda x, width: x.rjust(width)


class Table(object):
    def __init__(self, *args):
        self.columns = args
        self.rows = []
        self.col_width = [len(col) for col in args]
        self.styles = [LJUST] * len(args)

    def add_row(self, *args):
        # FIXME: check number of arguments
        self.rows.append(args)
        for i, col in enumerate(args):
            linelen = max(len(line) for line in col.splitlines())
            self.col_width[i] = max(linelen, self.col_width[i])

    def render(self):
        widths = self.col_width

        def _render_row(row, header=False):
            cells = []
            for col, value in enumerate(row):
                style = CENTER if header else self.styles[col]
                width = widths[col]
                cells += [style(value, width)]
            return u'| ' + u' | '.join(cells) + u' |\n'

        def _render_separator():
            cells = [u'-' * widths[i] for i in xrange(len(self.columns))]
            return u'+-' + u'-+-'.join(cells) + u'-+\n'

        s = _render_separator()
        s += _render_row(self.columns, header=True)
        s += _render_separator()
        for row in self.rows:
            s += _render_row(row)
        s += _render_separator()
        return s
