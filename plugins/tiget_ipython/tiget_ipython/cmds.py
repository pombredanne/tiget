import IPython

import tiget
from tiget.cmds import cmd
from tiget.settings import settings
from tiget.plugins import plugins


@cmd()
def ipython_cmd(opts):
    """
    start embedded ipython shell

    SYNOPSIS
        ipython
    """
    ns = {}
    for plugin in plugins.itervalues():
        models = plugin.models
        ns.update({model.__name__: model for model in models.itervalues()})
    config = IPython.frontend.terminal.ipapp.load_default_config()
    config.InteractiveShellEmbed = config.TerminalInteractiveShell
    config.PromptManager.in_template = settings.ipython.prompt
    if not settings.core.color:
        config.InteractiveShellEmbed.colors = 'NoColor'
    config.InteractiveShellEmbed.confirm_exit = False
    IPython.embed(
        user_module=tiget, user_ns=ns, config=config, display_banner=False)
