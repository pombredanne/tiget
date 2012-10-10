import sys

import tiget
from tiget.plugins.api import *
from tiget.conf import settings
from tiget.git import find_repository, GitError

__author__ = tiget.__author__
__version__ = tiget.__version__


class RepositorySetting(Setting):
    def clean(self, value):
        try:
            return find_repository(value)
        except GitError as e:
            raise ValueError(e)

    def format(self, repo):
        if repo:
            return repo.path
        return super().format(None)


def load(plugin):
    from tiget.core import cmds
    plugin.add_cmds(cmds)
    plugin.add_settings(
        branchname=StrSetting(default='tiget'),
        debug=BoolSetting(default=False),
        color=BoolSetting(default=sys.stdout.isatty()),
        pdb_module=StrSetting(default='pdb'),
        repository=RepositorySetting(),
    )
    try:
        settings.core.repository = '.'
    except ValueError:
        pass
