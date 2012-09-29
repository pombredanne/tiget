import sys

__author__ = 'Martin Natano <natano@natano.net>'
__version__ = '0.1a0'


def init_plugin():
    from tiget_git_import.git_import import GitImporter, PATH_PREFIX
    sys.path_hooks.append(GitImporter)
    sys.path.append('{}/config'.format(PATH_PREFIX))
