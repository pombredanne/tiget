import os
import sys
import fcntl
import termios
import struct
import traceback
from io import StringIO
from importlib import import_module
from collections import namedtuple
from tempfile import NamedTemporaryFile

from colors import red
from git_orm import transaction, GitError

from tiget.conf import settings

__all__ = [
    'open_in_editor', 'paginate', 'get_termsize', 'print_error', 'post_mortem',
    'load_file',
]


def open_in_editor(content):
    with NamedTemporaryFile(prefix='tiget') as f:
        f.write(content.encode('utf-8'))
        f.seek(0)
        os.system('{} {}'.format(settings.core.editor, f.name))
        content = f.read().decode('utf-8')
    return content


def paginate(content):
    geometry = get_termsize()
    needs_pagination = False
    # TODO: better performance; consider long lines
    if len(content.splitlines()) > geometry.lines - 1:
        needs_pagination = True
    if needs_pagination:
        with NamedTemporaryFile(prefix='tiget') as f:
            f.write(content.encode('utf-8'))
            f.seek(0)
            os.system('{} {}'.format(settings.core.pager, f.name))
    else:
        print(content, end='')


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
    print_error('internal error (see traceback)')
    traceback.print_exc()
    if settings.core.debug:
        try:
            pdb = import_module(settings.core.pdb_module)
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
            with transaction.wrap() as trans:
                path = filename[len('tiget:'):].strip('/').split('/')
                content = trans.get_blob(path).decode('utf-8')
        except GitError:
            raise IOError('No such file: \'{}\''.format(filename))
        f = StringIO(content)
        f.name = filename
        return f
    return open(os.path.expanduser(filename))
