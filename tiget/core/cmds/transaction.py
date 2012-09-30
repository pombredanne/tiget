from tiget import git
from tiget.cmds import cmd, CmdError


@cmd()
def begin_cmd(opts):
    """
    begin transaction

    SYNOPSIS
        begin
    """
    if git.transaction:
        raise CmdError('there is already a transaction running')
    git.transaction = git.Transaction()


@cmd()
def commit_cmd(opts, message=None):
    """
    commit transaction

    SYNOPSIS
        commit [MESSAGE]
    """
    if not git.transaction:
        raise CmdError('no transaction running')
    try:
        git.transaction.commit(message)
    except git.GitError as e:
        raise CmdError(e)
    git.transaction = None


@cmd()
def rollback_cmd(opts):
    """
    roll back transaction

    SYNOPSIS
        rollback
    """
    if not git.transaction:
        raise CmdError('no transaction running')
    git.transaction.rollback()
    git.transaction = None
