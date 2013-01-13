from tiget.plugins.settings import *
from tiget.git import get_config


def load(plugin):
    from tiget.scrum import models, cmds
    plugin.add_models(models)
    plugin.add_cmds(cmds)
    plugin.add_setting(
        'current_user', StrSetting(default=get_config('user.email')))
