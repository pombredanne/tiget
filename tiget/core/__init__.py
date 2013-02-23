import os
import sys

from tiget.plugins.settings import *
from tiget.conf import settings
from tiget.git import find_repository, GitError
from tiget.script import Script


class RepositorySetting(Setting):
    def clean(self, value):
        if not value is None:
            try:
                value = find_repository(value)
            except GitError as e:
                raise ValueError(e)
        return value

    def load_config(self, filename):
        try:
            script = Script.from_file(filename)
        except IOError:
            pass
        else:
            script.run()

    def changed(self, repo):
        if repo:
            self.load_config('tiget:/config/tigetrc')
            if repo.workdir:
                self.load_config(os.path.join(repo.workdir, '.tigetrc'))

    def format(self, repo):
        if repo:
            return repo.path
        return super().format(None)


def load(plugin):
    from tiget.core import cmds
    plugin.add_cmds(cmds)
    plugin.add_settings(
        branch=StrSetting(default='tiget'),
        remote=StrSetting(default='origin'),
        debug=BoolSetting(default=False),
        color=BoolSetting(default=sys.stdout.isatty()),
        editor=StrSetting(default=os.environ.get('EDITOR', 'vi')),
        history_file=StrSetting(default='~/.tiget_history'),
        history_limit=IntSetting(default=1000),
        pager=StrSetting(default=os.environ.get('PAGER', 'less')),
        pdb_module=StrSetting(default='pdb'),
        repository=RepositorySetting(),
    )
    try:
        settings.core.repository = '.'
    except ValueError:
        pass
