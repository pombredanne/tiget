import os, stat, time
from dulwich.repo import Repo, NotGitRepository
from dulwich.objects import Blob, Tree, Commit
from tiget import settings
from tiget.version import VERSIONSTR
from tiget.cmd_registry import cmd_registry, Cmd, CmdError

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
            repo = Repo(os.getcwd())
        except NotGitRepository:
            raise self.error('no git repository')
        ref = 'refs/heads/{0}'.format(settings.branchname)
        if ref in repo.refs:
            raise self.error('already initialized')

        fileperm = stat.S_IFREG | 0644
        dirperm = stat.S_IFDIR

        tree = Tree()
        version = Blob.from_string('{0}\n'.format(VERSIONSTR))
        tree.add('VERSION', fileperm, version.id)
        tickets = Tree()
        keep = Blob.from_string('')
        tickets.add('.keep', fileperm, keep.id)
        tree.add('tickets', dirperm, tickets.id)

        commit = Commit()
        commit.tree = tree.id
        commit.author = commit.committer = 'fix me <fixme@example.com>'
        commit.author_time = commit.commit_time = int(time.time())
        timezone = time.timezone
        if time.daylight and time.localtime().tm_isdst:
            timezone = time.altzone
        commit.author_timezone = commit.commit_timezone = timezone
        commit.encoding = 'UTF-8'
        commit.message = 'Initial commit'

        repo.object_store.add_object(version)
        repo.object_store.add_object(keep)
        repo.object_store.add_object(tickets)
        repo.object_store.add_object(tree)
        repo.object_store.add_object(commit)
        repo.refs['refs/heads/%s' % settings.branchname] = commit.id

@cmd_registry.add
class HelpCmd(Cmd):
    """
    usage: help [cmd]

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
class VersionCmd(Cmd):
    """
    usage: version

    Prints the version. Can be used for version detection in command line
    scripts.
    """
    name = 'version'
    help_text = 'print version information'

    @Cmd.argcount(0)
    def do(self, opts, args):
        print VERSIONSTR
