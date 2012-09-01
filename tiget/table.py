from collections import namedtuple
from tiget.utils import get_termsize

class Table(object):
    def __init__(self, *args):
        self.columns = args
        self.rows = []

    def add_row(self, *args):
        assert len(args) == len(self.columns)
        self.rows.append(args)
    
    def get_widths(self):
        widths = []
        for i, col in enumerate(self.columns):
            width = len(col)
            for row in self.rows:
                linelen = max(len(line) for line in row[i].splitlines())
                width = max(linelen, width)
            widths += [width]
        return widths

    def render(self):
        widths = self.get_widths()
        print u' | '.join(col.center(widths[i]) for i, col in enumerate(self.columns))
        print u'-+-'.join(u'-' * widths[i] for i in xrange(len(self.columns)))
        for row in self.rows:
            print u' | '.join(col.ljust(widths[i]) for i, col in enumerate(row))
