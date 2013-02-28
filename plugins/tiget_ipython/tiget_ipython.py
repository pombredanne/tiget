from IPython import embed
from IPython.frontend import terminal

from tiget.cmds import Cmd
from tiget.conf import settings
from tiget.plugins import plugins
from tiget.plugins.settings import *


class IPythonCmd(Cmd):
    description = 'start embedded ipython shell'
    names = ('ipython',)

    def do(self, args):
        ns = {}
        for plugin in plugins.values():
            models = plugin.models
            ns.update({model.__name__: model for model in models.values()})
        config = terminal.ipapp.load_default_config()
        config.InteractiveShellEmbed = config.TerminalInteractiveShell
        config.PromptManager.in_template = settings.ipython.prompt
        if not settings.core.color:
            config.InteractiveShellEmbed.colors = 'NoColor'
        config.InteractiveShellEmbed.confirm_exit = False
        embed(user_ns=ns, config=config, display_banner=False)


def load(plugin):
    plugin.add_cmd(IPythonCmd)
    plugin.add_setting('prompt', StrSetting(default='IPython [\\#]: '))


def unload(plugin):
    terminal.embed._embedded_shell = None
