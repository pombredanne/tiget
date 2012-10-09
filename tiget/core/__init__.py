import sys

import tiget
from tiget.plugins.api import *

__author__ = tiget.__author__
__version__ = tiget.__version__


def load(plugin):
    from tiget.core import cmds
    plugin.add_cmds(cmds)
    plugin.add_settings(
        branchname=StrSetting(default='tiget'),
        debug=BoolSetting(default=False),
        color=BoolSetting(default=sys.stdout.isatty()),
        pdb_module=StrSetting(default='pdb'),
        repository_path=StrSetting(default='.'),
    )
