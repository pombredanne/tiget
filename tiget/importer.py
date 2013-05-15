import imp
import sys

from git_orm.importer import GitImporter, PATH_PREFIX


DEFAULT_PATH = '{}/config'.format(PATH_PREFIX)


def load(plugin):
    sys.path_hooks.append(GitImporter)
    if not DEFAULT_PATH in sys.path:
        sys.path.append(DEFAULT_PATH)


def unload(plugin):
    if DEFAULT_PATH in sys.path:
        sys.path.remove(DEFAULT_PATH)
    sys.path_hooks.remove(GitImporter)
