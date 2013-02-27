import sys

from tiget.git import init_repo, GitError
from tiget.utils import print_error, post_mortem
from tiget.plugins import load_plugin


def main():
    load_plugin('tiget.core')
    try:
        init_repo()
    except GitError as e:
        print_error(e)
        sys.exit(1)
    except Exception as e:
        post_mortem()
        sys.exit(1)
