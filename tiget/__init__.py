VERSION = (0, 1, 'alpha', 0)

def get_version():
    version = '.'.join(str(x) for x in VERSION[:2])
    if not VERSION[2] == 'final':
        version += VERSION[2][0] + str(VERSION[3])
    elif VERSION[3] > 0:
        version += '.post' + str(VERSION[3])
    return version

def _init():
    from . import cmds

_init()
