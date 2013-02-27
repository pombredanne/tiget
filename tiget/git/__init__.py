import pkg_resources

from tiget.conf import settings


class GitError(Exception): pass


def get_config(name):
    repo = settings.core.repository
    if repo is None:
        raise GitError('core.repository is not set')
    return repo.config[name]


def init_repo():
    from tiget.git import transaction

    with transaction.wrap():
        trans = transaction.current(initialized=False)
        tigetrc = pkg_resources.resource_string('tiget', 'data/tigetrc')
        trans.set_blob(['config', 'tigetrc'], tigetrc)
        trans.add_message('Initialize Repository')
        trans.is_initialized = True
