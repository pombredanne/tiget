import sys

__author__ = 'Martin Natano <natano@natano.net>'
__version__ = '0.1a0'


def init_plugin(plugin):
    from tiget_git_import.git_import import GitImporter, PATH_PREFIX
    sys.path_hooks.append(GitImporter)
    path = '{}/config'.format(PATH_PREFIX)
    if not path in sys.path:
        sys.path.append(path)
