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

def serialize(data):
    s = u''
    for k, v in data.iteritems():
        value = v or u''
        s += u'{0}: {1}\n'.format(k, value.replace(u'\n', u'\n    '))
    return s

def deserialize(s):
    data = {}
    for paragraph in re.split(r'\n(?!\s)', s):
        if paragraph.startswith(u'#') or paragraph == u'':
            continue
        m = re.match(r'(\w+):\s?(.*?)$(.+)?', paragraph, re.MULTILINE | re.DOTALL)
        if not m:
            raise ValueError('syntax error')
        key = m.group(1)
        value = m.group(2)
        if m.group(3):
            value += textwrap.dedent(m.group(3))
        data[key] = value
    return data
