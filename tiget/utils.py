import os
import sys
import re
import textwrap
import fcntl
import termios
import struct
import subprocess
from collections import namedtuple
from tempfile import NamedTemporaryFile

from colors import red

from tiget.settings import settings


def open_in_editor(content):
    editor = os.environ.get('EDITOR', 'vi')
    with NamedTemporaryFile(prefix='tiget') as f:
        f.write(content.encode('utf-8'))
        f.seek(0)
        os.system('{} {}'.format(editor, f.name))
        content = f.read().decode('utf-8')
    return content


TerminalGeometry = namedtuple('TerminalGeometry', ('lines', 'cols'))

def get_termsize(fd=1):
    try:
        geometry = struct.unpack(
            'hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except IOError:
        geometry = (25, 80)
    return TerminalGeometry(*geometry)


class Serializer(object):
    ITEM_SEPARATOR = re.compile(r'\n(?!\s)')
    ITEM_MATCHER = re.compile(
        r'(?P<key>\w+):\s?(?P<value>.*?)$(?P<value2>.+)?',
        re.MULTILINE | re.DOTALL)

    def dumps(self, data):
        s = u''
        for k, v in data.iteritems():
            value = v or u''
            s += u'{}: {}\n'.format(k, value.replace(u'\n', u'\n    '))
        return s

    def loads(self, s):
        data = {}
        lineno = 0
        for item in self.ITEM_SEPARATOR.split(s):
            if not item.startswith(u'#') and item.strip():
                m = self.ITEM_MATCHER.match(item)
                if not m:
                    raise ValueError(
                        'syntax error on line {}'.format(lineno + 1))
                value = m.group('value')
                value += textwrap.dedent(m.group('value2') or u'')
                data[m.group('key')] = value or None
            lineno += item.count(u'\n') + 1
        return data

serializer = Serializer()


RESERVED_CHARS = u'/\\|?*<>:+[]"\u0000%'

def quote_filename(name):
    quoted = ''
    for c in name:
        if c in RESERVED_CHARS:
            for byte in c.encode('utf-8'):
                quoted += '%' + byte.encode('hex')
        else:
            quoted += c.encode('utf-8')
    return quoted


def unquote_filename(name):
    raw = re.sub(r'%([\da-f]{2})', lambda m: m.group(1).decode('hex'), name)
    return raw.decode('utf-8')


def print_error(line):
    if settings.color:
        line = red(line)
    print >> sys.stderr, line


def find_repository_path(cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    head, tail = cwd, '.'
    while tail:
        if os.path.exists(os.path.join(head, '.git')):
            return head
        head, tail = os.path.split(head)
