import os
import re
import textwrap
import fcntl
import termios
import struct
import subprocess
from tempfile import NamedTemporaryFile


def open_in_editor(content):
    editor = os.environ.get('EDITOR', 'vi')
    with NamedTemporaryFile(prefix='tiget') as f:
        f.write(content.encode('utf-8'))
        f.seek(0)
        os.system('{0} {1}'.format(editor, f.name))
        content = f.read().decode('utf-8')
    return content


def get_termsize(fd=1):
    return struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))


class Serializer(object):
    ITEM_SEPARATOR = re.compile(r'\n(?!\s)')
    ITEM_MATCHER = re.compile(
        r'(?P<key>\w+):\s?(?P<value>.*?)$(?P<value2>.+)?',
        re.MULTILINE | re.DOTALL)

    def dumps(self, data):
        s = u''
        for k, v in data.iteritems():
            value = v or u''
            s += u'{0}: {1}\n'.format(k, value.replace(u'\n', u'\n    '))
        return s

    def loads(self, s):
        data = {}
        lineno = 0
        for item in self.ITEM_SEPARATOR.split(s):
            if not item.startswith(u'#') and item.strip():
                m = self.ITEM_MATCHER.match(item)
                if not m:
                    raise ValueError(
                        'syntax error on line {0}'.format(lineno + 1))
                value = m.group('value')
                value += textwrap.dedent(m.group('value2') or u'')
                data[m.group('key')] = value or None
            lineno += item.count(u'\n') + 1
        return data

serializer = Serializer()
