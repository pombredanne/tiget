from tiget.git import find_repository_path, init_repo, GitError
from tiget.utils import print_error
from tiget.conf import settings


def main():
    try:
        settings.core.repository_path = find_repository_path()
        init_repo()
    except GitError as e:
        print_error(e)
        return 1
