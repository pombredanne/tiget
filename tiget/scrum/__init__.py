import tiget
from tiget.git import get_config
from tiget.plugins.api import *

__author__ = tiget.__author__
__version__ = tiget.__version__


def load(plugin):
    from tiget.scrum import models, cmds
    plugin.add_models(models)
    plugin.add_cmds(cmds)
    plugin.add_setting(
        'current_user', StrSetting(default=get_config('user.email')))
