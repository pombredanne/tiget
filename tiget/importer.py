import imp
import sys

import tiget
from tiget.git import auto_transaction, get_transaction, GitError

__author__ = tiget.__author__
__version__ = tiget.__version__


PATH_PREFIX = 'tiget-git-import:'
DEFAULT_PATH = '{}/config'.format(PATH_PREFIX)


def load(plugin):
    sys.path_hooks.append(GitImporter)
    if not DEFAULT_PATH in sys.path:
        sys.path.append(DEFAULT_PATH)


def unload(plugin):
    if DEFAULT_PATH in sys.path:
        sys.path.remove(DEFAULT_PATH)
    sys.path_hooks.remove(GitImporter)


class GitImporter(object):
    def __init__(self, path):
        if not path.startswith(PATH_PREFIX):
            raise ImportError()
        self.path = path[len(PATH_PREFIX):].rstrip('/')

    @auto_transaction()
    def get_filename(self, fullname, prefix=PATH_PREFIX):
        transaction = get_transaction()
        shortname = fullname.rpartition('.')[2]
        base = '/'.join([self.path, shortname])
        for ext in ('/__init__.py', '.py'):
            filename = base + ext
            if transaction.exists(filename.strip('/').split('/')):
                if prefix:
                    filename = prefix + filename
                return filename
        raise ImportError()

    def is_package(self, fullname):
        return self.get_filename(fullname).endswith('/__init__.py')

    @auto_transaction()
    def get_source(self, fullname):
        path = self.get_filename(fullname, prefix=None).strip('/').split('/')
        return get_transaction().get_blob(path).decode('utf-8') + '\n'

    @auto_transaction()
    def get_code(self, fullname):
        source = self.get_source(fullname)
        filename = self.get_filename(fullname)
        return compile(source, filename, 'exec')

    def find_module(self, fullname, path=True):
        try:
            self.get_filename(fullname)
        except ImportError:
            return None
        return self

    def load_module(self, fullname):
        with auto_transaction():
            code = self.get_code(fullname)
            is_pkg = self.is_package(fullname)
        is_reload = fullname in sys.modules
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = code.co_filename
        mod.__loader__ = self
        if is_pkg:
            path = '/'.join([PATH_PREFIX, fullname.rpartition('.')[2]])
            mod.__path__ = [path]
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        try:
            exec(code, mod.__dict__)
        except:
            if not is_reload:
                del sys.modules[fullname]
            raise
        return mod
