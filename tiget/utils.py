import os, re, textwrap
from tempfile import NamedTemporaryFile
import subprocess

def open_in_editor(content):
    editor = os.environ.get('EDITOR', 'vi')
    with NamedTemporaryFile(prefix='tiget') as f:
        f.write(content.encode('utf-8'))
        f.seek(0)
        os.system('{0} {1}'.format(editor, f.name))
        content = f.read().decode('utf-8')
    return content

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
        for item in self.ITEM_SEPARATOR.split(s):
            if item.startswith(u'#') or item == u'':
                continue
            m = self.ITEM_MATCHER.match(item)
            if not m:
                raise ValueError('syntax error')
            value = m.group('value')
            value2 = m.group('value2')
            if m.group('value2'):
                value += textwrap.dedent(m.group('value2'))
            data[m.group('key')] = value
        return data

serializer = Serializer()
