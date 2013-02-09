from nose.tools import *
from nose.plugins.skip import SkipTest
from mock import Mock, patch

from tiget import adapter


class Foo: pass


class TestAdapterRegistry:
    def setup(self):
        self.adapter = Mock()
        self.adapter2 = Mock()
        self.registry = adapter.AdapterRegistry()

    def test_register(self):
        self.registry.register('trait', Foo, self.adapter)
        eq_(self.registry.adapters, {('trait', Foo): [self.adapter]})

    def test_register_partial(self):
        decorator = self.registry.register('trait', Foo)
        eq_(self.registry.adapters, {})
        decorator(self.adapter)
        eq_(self.registry.adapters, {('trait', Foo): [self.adapter]})

    def test_register_multi(self):
        self.registry.register('trait', Foo, self.adapter)
        self.registry.register('trait', Foo, self.adapter2)
        eq_(self.registry.adapters, {('trait', Foo): [self.adapter2, self.adapter]})
        self.registry.register('trait', Foo, self.adapter)
        eq_(self.registry.adapters, {('trait', Foo): [self.adapter, self.adapter2]})

    def test_unregister(self):
        self.registry.register('trait', Foo, self.adapter)
        self.registry.unregister('trait', Foo, self.adapter)
        eq_(self.registry.adapters, {})

    def test_unregister_non_existant(self):
        assert_raises(
            adapter.AdapterNotFound,
            self.registry.unregister, 'trait', Foo, self.adapter)

    def test_get_adapter(self):
        self.registry.register('trait', Foo, self.adapter)
        eq_(self.registry.get_adapter('trait', Foo), self.adapter)

    def test_get_adapter_multi_adapters(self):
        self.registry.register('trait', Foo, self.adapter)
        self.registry.register('trait', Foo, self.adapter2)
        eq_(self.registry.get_adapter('trait', Foo), self.adapter2)

    def test_get_adapter_multi_traits(self):
        self.registry.register('trait', Foo, self.adapter)
        self.registry.register('trait2', Foo, self.adapter2)
        eq_(self.registry.get_adapter('trait', Foo), self.adapter)

    def test_get_adapter_mro(self):
        raise SkipTest()

    def test_get(self):
        self.adapter.return_value = 42
        foo = Foo()
        self.registry.register('trait', Foo, self.adapter)
        eq_(self.registry.get('trait', foo), 42)
        self.adapter.assert_called_once_with(foo)
