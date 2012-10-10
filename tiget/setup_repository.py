from tiget.git import init_repo, GitError
from tiget.utils import print_error
from tiget.conf import settings


def main():
    try:
        init_repo()
    except GitError as e:
        print_error(e)
        return 1
