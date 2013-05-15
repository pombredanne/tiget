import pkg_resources

from tiget.conf import settings


class GitError(Exception): pass


def get_config(name):
    repo = settings.core.repository
    if repo is None:
        raise GitError('no repository found')
    return repo.config[name]


def is_repo_initialized():
    repo = settings.core.repository
    if repo is None:
        return False
    ref = 'refs/heads/{}'.format(settings.core.branch)
    try:
        repo.lookup_reference(ref)
    except KeyError:
        return False
    return True


def init_repo():
    from git_orm import transaction

    if is_repo_initialized():
        raise GitError('repository is already initialized')

    with transaction.wrap() as trans:
        tigetrc = pkg_resources.resource_string('tiget', 'data/tigetrc')
        trans.set_blob(['config', 'tigetrc'], tigetrc)
        trans.add_message('Initialize Repository')
