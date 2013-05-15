import os
import sys

import git_orm

from tiget.plugins.settings import *


class RepositorySetting(Setting):
    def clean(self, value):
        try:
            git_orm.set_repository(value)
        except git_orm.GitError as e:
            raise ValueError(e)
        return git_orm.get_repository()

    def format(self, repo):
        repo = git_orm.get_repository()
        path = repo.path if repo else None
        return super().format(path)


class BranchSetting(Setting):
    def clean(self, value):
        git_orm.set_branch(value)
        return git_orm.get_branch()

    def format(self, repo):
        return super().format(git_orm.get_branch())


class RemoteSetting(Setting):
    def clean(self, value):
        git_orm.set_remote(value)
        return git_orm.get_remote()

    def format(self, repo):
        return super().format(git_orm.get_remote())


def load(plugin):
    from tiget.core import cmds
    plugin.add_cmds(cmds)
    plugin.add_settings(
        branch=BranchSetting(),
        remote=RemoteSetting(),
        debug=BoolSetting(default=False),
        color=BoolSetting(default=sys.stdout.isatty()),
        editor=StrSetting(default=os.environ.get('EDITOR', 'vi')),
        history_file=StrSetting(default='~/.tiget_history'),
        history_limit=IntSetting(default=1000),
        pager=StrSetting(default=os.environ.get('PAGER', 'less')),
        pdb_module=StrSetting(default='pdb'),
        repository=RepositorySetting(),
    )
    plugin.settings.branch = 'tiget'
    plugin.settings.remote = 'origin'
    try:
        plugin.settings.repository = '.'
    except ValueError:
        pass
