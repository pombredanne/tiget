import os
from tempfile import NamedTemporaryFile
import subprocess

def edit_content(content):
    try:
        editor = os.environ['EDITOR']
    except KeyError:
        editor = 'vi'
    with NamedTemporaryFile(prefix='tiget') as f:
        f.write(content.encode('utf-8'))
        f.seek(0)
        os.system('{0} {1}'.format(editor, f.name))
        content = f.read().decode('utf-8')
    return content
