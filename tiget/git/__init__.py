from pkg_resources import Requirement, resource_string

import pygit2

from tiget.conf import settings


class GitError(Exception):
    pass


def find_repository(cwd='.'):
    try:
        path = pygit2.discover_repository(cwd)
        return pygit2.Repository(path)
    except KeyError:
        raise GitError('no repository found in "{}"'.format(cwd))


def get_config(name):
    repo = settings.core.repository
    if repo is None:
        raise GitError('core.repository is not set')
    return repo.config[name]


def init_repo():
    from tiget import __version__
    from tiget.git import transaction

    with transaction.wrap():
        trans = transaction.current(initialized=False)

        version = '{}\n'.format(__version__)
        trans.set_blob(['config', 'VERSION'], version.encode('utf-8'))

        req = Requirement.parse('tiget')
        tigetrc = resource_string(req, 'tiget/config/tigetrc')
        trans.set_blob(['config', 'tigetrc'], tigetrc)

        trans.add_message('Initialize Repository')
        trans.is_initialized = True
