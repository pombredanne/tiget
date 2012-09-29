import IPython

import tiget
from tiget.cmds import cmd
from tiget.models.base import models
from tiget.settings import settings


@cmd()
def ipython_cmd(opts):
    """
    start embedded ipython shell

    SYNOPSIS
        ipython
    """
    ns = {model.__name__: model for model in models.itervalues()}
    config = IPython.frontend.terminal.ipapp.load_default_config()
    config.InteractiveShellEmbed = config.TerminalInteractiveShell
    config.PromptManager.in_template = 'IPython[\\#]> '
    if not settings.color:
        config.InteractiveShellEmbed.colors = 'NoColor'
    config.InteractiveShellEmbed.confirm_exit = False
    IPython.embed(
        user_module=tiget, user_ns=ns, config=config, display_banner=False)
