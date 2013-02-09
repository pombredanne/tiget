"""
Simple Adapter Implementation

This module provides a registry to work with adapters.

>>> from tiget import adapter
>>> class Octopus:
...     legs = 8
>>> @adapter.register('4-legged', Octopus)
... class MutantOctopus:
...     def __init__(self, octopus):
...         self.octopus = octopus
...     legs = 4
>>> tetrapod = adapter.get('4-legged', Octopus())
>>> tetrapod.legs
4
>>> type(tetrapod).__name__
'MutantOctopus'
>>> adapter.unregister('4-legged', Octopus, MutantOctopus)
>>> adapter.get_adapter('4-legged', Octopus)
Traceback (most recent call last):
    ...
tiget.adapter.AdapterNotFound: there is no adapter for Octopus implementing '4-legged'

"""


class AdapterNotFound(Exception):
    def __init__(self, trait, cls):
        return super().__init__('there is no adapter for {} implementing {!r}'
            .format(cls.__name__, trait))


class AdapterRegistry:
    def __init__(self):
        super().__init__()
        self.adapters = {}

    def register(self, trait, cls, adapter=None):
        def _decorator(adapter):
            adapters = self.adapters.setdefault((trait, cls), [])
            try:
                adapters.remove(adapter)
            except ValueError:
                pass
            adapters.insert(0, adapter)
            return adapter
        if not adapter is None:
            return _decorator(adapter)
        return _decorator

    def unregister(self, trait, cls, adapter):
        try:
            adapters = self.adapters[(trait, cls)]
            adapters.remove(adapter)
        except (KeyError, ValueError):
            raise AdapterNotFound(trait, cls)
        if not adapters:
            del self.adapters[(trait, cls)]

    def get_adapter(self, trait, cls):
        for cls_ in cls.__mro__:
            try:
                return self.adapters[(trait, cls_)][0]
            except KeyError:
                pass
        raise AdapterNotFound(trait, cls)

    def get(self, trait, obj):
        adapter = self.get_adapter(trait, type(obj))
        return adapter(obj)


_registry = AdapterRegistry()
register = _registry.register
unregister = _registry.unregister
get_adapter = _registry.get_adapter
get = _registry.get
