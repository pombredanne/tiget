from tiget.cmd_registry import cmd_registry, Cmd
from tiget.git import init_repo, GitError

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
