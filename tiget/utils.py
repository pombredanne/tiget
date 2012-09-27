import os
import sys
import re
import fcntl
import termios
import struct
import subprocess
import traceback
import imp
from collections import namedtuple
from tempfile import NamedTemporaryFile

from colors import red

from tiget.settings import settings
from tiget.git import auto_transaction, get_transaction, GitError

__all__ = [
    'open_in_editor', 'get_termsize', 'quote_filename', 'unquote_filename',
    'print_error', 'post_mortem', 'create_module', 'load_file',
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
        line = red(str(line))
    print >> sys.stderr, line


def post_mortem():
    traceback.print_exc()
    if settings.debug:
        try:
            pdb = __import__(settings.pdb_module)
        except ImportError as e:
            print_error(e)
        else:
            try:
                pdb.post_mortem()
            except KeyboardInterrupt:
                pass


def create_module(name):
    module = imp.new_module(name)
    sys.modules[name] = module
    return module


def load_file(filename):
    if filename.startswith('tiget:'):
        with auto_transaction():
            try:
                transaction = get_transaction()
                content = transaction.get_blob(filename[len('tiget:'):])
            except GitError as e:
                raise IOError('No such file: \'{}\''.format(filename))
    else:
        with open(filename) as f:
            content = f.read()
    return content
