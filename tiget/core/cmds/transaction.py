from tiget.git import begin, commit, rollback, GitError
from tiget.cmds import cmd, CmdError


@cmd()
def begin_cmd(opts):
    """
    begin transaction

    SYNOPSIS
        begin
    """
    try:
        begin()
    except GitError as e:
        raise CmdError(e)


@cmd()
def commit_cmd(opts, message=None):
    """
    commit transaction

    SYNOPSIS
        commit [MESSAGE]
    """
    try:
        commit(message)
    except GitError as e:
        raise CmdError(e)


@cmd()
def rollback_cmd(opts):
    """
    roll back transaction

    SYNOPSIS
        rollback
    """
    try:
        rollback()
    except GitError as e:
        raise CmdError(e)
