from subprocess import Popen

from tiget.git import GitError
from tiget.conf import settings


def fetch():
    cmd = ['git', 'fetch', settings.core.remote,
        'refs/heads/{0}:refs/remotes/origin/{0}'.format(settings.core.branch)]
    p = Popen(cmd, cwd=settings.core.repository.workdir)
    status = p.wait()
    if status:
        raise GitError('git-fetch returned with exit status {}'.format(status))


def push():
    cmd = ['git', 'push', settings.core.remote,
        'refs/heads/{0}:refs/heads/{0}'.format(settings.core.branch)]
    p = Popen(cmd, cwd=settings.core.repository.workdir)
    status = p.wait()
    if status:
        raise GitError('git-push returned with exit status {}'.format(status))


def merge():
    raise NotImplementedError
