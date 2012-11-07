from tiget.git import transaction, init_repo, GitError
from tiget.cmds import cmd, CmdError


@cmd()
def begin_cmd(opts):
    """
    begin transaction

    SYNOPSIS
        begin
    """
    try:
        transaction.begin()
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
        transaction.commit(message)
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
        transaction.rollback()
    except GitError as e:
        raise CmdError(e)


@cmd()
def init_repo_cmd(opts):
    """
    initialize repository

    SYNOPSIS
        init-repo
    """
    try:
        init_repo()
    except GitError as e:
        raise CmdError(e)
