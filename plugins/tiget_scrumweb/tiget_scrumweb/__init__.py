from pkg_resources import Requirement, resource_filename

import bottle
from tiget.plugins.api import *


def load(plugin):
    from tiget_scrumweb import cmds
    plugin.add_cmds(cmds)
    plugin.add_setting('password_file', StrSetting(default='.passwords'))

    req = Requirement.parse('tiget_scrumweb')
    tpl_path = resource_filename(req, 'tiget_scrumweb/templates')
    bottle.TEMPLATE_PATH = [tpl_path]
