from dulwich.repo import Repo
from tiget import settings
from tiget.version import VERSIONSTR
from tiget.cmd_registry import cmd_registry, Cmd, CmdError
from tiget.git import init_repo, GitError, GitTransaction

@cmd_registry.add
class AliasCmd(Cmd):
    """
    usage: alias [-d] ALIAS [CMD]
    """
    name = 'alias'
    help_text = 'define or list aliases'
    options = 'd'

    def do(self, opts, args):
        delete = False
        for opt, optarg in opts:
            if opt == '-d':
                delete = True
        if delete:
            if not len(args) == 1:
                raise self.argcount_error()
            alias = args[0]
            try:
                del settings.aliases[alias]
            except KeyError:
                raise CmdError('{0}: alias not found'.format(alias))
        else:
            if len(args) == 0:
                for alias in sorted(settings.aliases.keys()):
                    cmd = settings.aliases[alias]
                    print '{0}: {1}'.format(alias, cmd)
            elif len(args) == 2:
                settings.aliases[args[0]] = args[1]
            else:
                raise self.argcount_error()

@cmd_registry.add
class BeginCmd(Cmd):
    """
    usage: begin
    """
    name = 'begin'
    help_text = 'begin transaction'

    @Cmd.argcount(0)
    def do(self, opts, args):
        if settings.transaction:
            raise self.error('there is already a transaction running')
        settings.transaction = GitTransaction()

@cmd_registry.add
class CommitCmd(Cmd):
    """
    usage: commit [MESSAGE]
    """
    name = 'commit'
    help_text = 'commit transaction'

    @Cmd.argcount(0, 1)
    def do(self, opts, args):
        if not settings.transaction:
            raise self.error('no transaction running')
        message = None
        if args:
            message = args[0]
        try:
            settings.transaction.commit(message)
        except GitError as e:
            raise self.error(e)
        settings.transaction = None

@cmd_registry.add
class InitCmd(Cmd):
    """
    usage: init

    Initializes the git repository for usage with tiget.
    """
    name = 'init'
    help_text = 'initialize the repository'

    @Cmd.argcount(0)
    def do(self, opts, args):
        try:
            init_repo()
        except GitError as e:
            raise self.error(e)

@cmd_registry.add
class HelpCmd(Cmd):
    """
    usage: help [CMD]

    Print the list of commands when no argument is given.
    Print the usage for <cmd> otherwise.
    """
    name = 'help'
    help_text = 'show this help page'

    @Cmd.argcount(0, 1)
    def do(self, opts, args):
        if not args:
            for name in sorted(cmd_registry.keys()):
                cmd = cmd_registry[name]
                print '{0}\t- {1}'.format(cmd.name, cmd.help_text)
        else:
            name = args[0]
            try:
                cmd = cmd_registry[name]
            except KeyError:
                raise CmdError('{0}: command not found'.format(name))
            usage = cmd.usage
            if usage:
                print usage
            else:
                raise CmdError('{0}: no usage information found'.format(name))

@cmd_registry.add
class RollbackCmd(Cmd):
    """
    usage: rollback
    """
    name = 'rollback'
    help_text = 'roll back transaction'

    @Cmd.argcount(0)
    def do (self, opts, args):
        if not settings.transaction:
            raise self.error('no transaction running')
        settings.transaction.rollback()
        settings.transaction = None

@cmd_registry.add
class VersionCmd(Cmd):
    """
    usage: version

    Print the version. Can be used for version detection in command line
    scripts.
    """
    name = 'version'
    help_text = 'print version information'

    @Cmd.argcount(0)
    def do(self, opts, args):
        print VERSIONSTR
