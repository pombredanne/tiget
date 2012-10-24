from pkg_resources import Requirement, resource_string

import pygit2

from tiget.conf import settings
from tiget.git.transaction import (
    GitError, begin, commit, rollback, get_transaction, auto_transaction)


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


@auto_transaction()
def init_repo():
    from tiget import __version__
    transaction = get_transaction(initialized=False)

    version_string = '{}\n'.format(__version__)
    transaction.set_blob(['config', 'VERSION'], version_string.encode('utf-8'))

    req = Requirement.parse('tiget')
    tigetrc = resource_string(req, 'tiget/config/tigetrc')
    transaction.set_blob(['config', 'tigetrc'], tigetrc)

    transaction.add_message('Initialize Repository')
    transaction.is_initialized = True
