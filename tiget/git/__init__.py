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
    from tiget.git import transaction

    with transaction.wrap():
        trans = transaction.current(initialized=False)
        tigetrc = '# put your initialization code here\n'
        trans.set_blob(['config', 'tigetrc'], tigetrc.encode('utf-8'))
        trans.add_message('Initialize Repository')
        trans.is_initialized = True
