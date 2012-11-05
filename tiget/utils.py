import os
import sys
import fcntl
import termios
import struct
import traceback
from collections import namedtuple
from tempfile import NamedTemporaryFile

from colors import red

from tiget.conf import settings
from tiget.git import transaction, GitError

__all__ = [
    'open_in_editor', 'get_termsize', 'print_error', 'post_mortem', 'load_file',
]


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


def print_error(line):
    if settings.core.color:
        line = red(str(line))
    print(line, file=sys.stderr)


def post_mortem():
    traceback.print_exc()
    if settings.core.debug:
        try:
            pdb = __import__(settings.core.pdb_module)
        except ImportError as e:
            print_error(e)
        else:
            try:
                pdb.post_mortem(sys.exc_info()[2])
            except KeyboardInterrupt:
                pass


def load_file(filename):
    if filename.startswith('tiget:'):
        try:
            with transaction.wrap():
                path = filename[len('tiget:'):].strip('/').split('/')
                content = transaction.current().get_blob(path).decode('utf-8')
        except GitError as e:
            raise IOError('No such file: \'{}\''.format(filename))
    else:
        with open(filename) as f:
            content = f.read()
    return content
