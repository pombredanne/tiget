import sys
from pkg_resources import Requirement, resource_listdir, resource_string

import tiget
from tiget.git import auto_transaction, get_transaction, GitError
from tiget.settings import settings
from tiget.utils import print_error


@auto_transaction()
def main():
    settings.color = sys.stdout.isatty()

    try:
        transaction = get_transaction(initialized=False)
    except GitError as e:
        print_error(e)
        return 1

    version_string = u'{}\n'.format(tiget.__version__)
    transaction.set_blob('/config/VERSION', version_string.encode('utf-8'))

    req = Requirement.parse('tiget')
    files = ['tigetrc', 'models.py', 'cmds.py']
    for filename in files:
        content = resource_string(req, 'tiget/config/{}'.format(filename))
        transaction.set_blob('/config/{}'.format(filename), content)

    transaction.add_message(u'Initialize Repository')
    transaction.is_initialized = True
