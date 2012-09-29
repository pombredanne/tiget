import IPython

import tiget
from tiget.cmds import Cmd
from tiget.models.base import models
from tiget.settings import settings


class IpythonCmd(Cmd):
    """
    usage: ipython
    """
    help_text = 'start embedded ipython shell'

    def do(self, opts):
        ns = {}
        for model in models.itervalues():
            ns[model.__name__] = model
        config = IPython.frontend.terminal.ipapp.load_default_config()
        config.InteractiveShellEmbed = config.TerminalInteractiveShell
        config.PromptManager.in_template = 'IPython[\\#]> '
        if not settings.color:
            config.InteractiveShellEmbed.colors = 'NoColor'
        config.InteractiveShellEmbed.confirm_exit = False
        IPython.embed(
            user_module=tiget, user_ns=ns, config=config, display_banner=False)
