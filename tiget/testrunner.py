import nose

from tiget.plugins import load_plugin


def collector():
    load_plugin('tiget.core')
    return nose.collector()
