import sys
import re
from subprocess import list2cmdline

from tiget.script import Script, Repl
from tiget.settings import settings
from tiget.utils import print_error, post_mortem, create_module, get_python_files
from tiget.git import auto_transaction, get_transaction, GitError, find_repository_path


@auto_transaction()
def load_config():
    transaction = get_transaction()

    config_module = create_module('config')
    files = get_python_files(transaction.list_blobs('/config'))
    for filename in files:
        name = re.match(r'(?:\d+-)?(.*)\.py', filename).group(1)
        filename = '/config/{}'.format(filename)
        content = transaction.get_blob(filename) + '\n'
        m = create_module('.'.join([config_module.__name__, name]))
        try:
            code = compile(content, filename, 'exec')
            exec(code, m.__dict__)
        except Exception as e:
            post_mortem()
            sys.exit(1)
        setattr(config_module, name, m)


def main():
    settings.color = sys.stdout.isatty()

    try:
        settings.repository_path = find_repository_path()
        load_config()
    except GitError as e:
        print_error(e)
        return 1

    args = sys.argv[1:]
    if args:
        script = Script(list2cmdline(args), '<argv>')
    else:
        if sys.stdin.isatty():
            script = Repl()
        else:
            script = Script(sys.stdin, '<stdin>')
    return script.run()
