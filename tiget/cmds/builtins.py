from tiget import settings, get_version
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
        print get_version()
