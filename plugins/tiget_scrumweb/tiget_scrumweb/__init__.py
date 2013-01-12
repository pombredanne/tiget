import os
from pkg_resources import Requirement, resource_filename

import bottle
from cork import Cork

from tiget.conf import settings
from tiget.plugins.api import *


def initialize():
    conf_file = os.path.expanduser(settins.scrumweb.password_file)
    if not os.path.exists(conf_file):
        with open(conf_file, 'w') as f:
            f.write('')


def load(plugin):
    from tiget_scrumweb import cmds
    plugin.add_cmds(cmds)
    plugin.add_setting('password_file', StrSetting(default='.passwords'))

    req = Requirement.parse('tiget_scrumweb')
    tpl_path = resource_filename(req, 'tiget_scrumweb/templates')
    bottle.TEMPLATE_PATH = [tpl_path]
