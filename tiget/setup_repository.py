import sys

from tiget.git import auto_transaction, get_transaction, GitError
from tiget.settings import settings
from tiget import get_version
from tiget.utils import print_error


@auto_transaction()
def main():
    settings.color = sys.stdout.isatty()

    try:
        transaction = get_transaction(initialized=False)
    except GitError as e:
        print_error(e)
        return 1

    version_string = u'{}\n'.format(get_version())
    transaction.set_blob('/VERSION', version_string.encode('utf-8'))

    transaction.add_message(u'Initialize Repository')
    transaction.is_initialized = True
