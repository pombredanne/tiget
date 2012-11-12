from nose.tools import *

from tiget.serializer import dumps, loads


class TestDump(object):
    def test_dumps_none(self):
        s = dumps({'none': None})
        eq_(s, 'none: \n')

    def test_dumps_oneline(self):
        s = dumps({'oneline': 'foo'})
        eq_(s, 'oneline: foo\n')

    def test_dumps_multiline(self):
        s = dumps({'multiline': 'foo\nbar\nbaz'})
        eq_(s, 'multiline: foo\n    bar\n    baz\n')


class TestLoad(object):
    def test_loads_none(self):
        data = loads('none: ')
        eq_(len(data), 1)
        eq_(data['none'], None)

    def test_loads_oneline(self):
        data = loads('oneline: foo')
        eq_(len(data), 1)
        eq_(data['oneline'], 'foo')

    def test_loads_multiline(self):
        data = loads('multiline: foo\n    bar\n    baz')
        eq_(len(data), 1)
        eq_(data['multiline'], 'foo\nbar\nbaz')

    def test_loads_comment(self):
        data = loads('# foo')
        eq_(len(data), 0)

    def test_loads_multiline_comment(self):
        data = loads('# foo\n    bar\n    baz')
        eq_(len(data), 0)

    def test_loads_blankline(self):
        data = loads('')
        eq_(len(data), 0)

    def test_loads_blankline_with_space(self):
        data = loads(' ')
        eq_(len(data), 0)

    def test_loads_broken(self):
        assert_raises(ValueError, loads, 'b0rked')


class TestDumpLoad(object):
    def dump_load(self, **data):
        s = dumps(data)
        restored = loads(s)
        eq_(len(data), len(restored))
        eq_(data.keys(), restored.keys())
        for key in data.keys():
            eq_(data[key], restored[key])

    def test_none(self):
        self.dump_load(nada=None)

    def test_oneline(self):
        self.dump_load(oneline='foo')

    def test_multiline(self):
        self.dump_load(multiline='foo\nbar\nbaz')

    def test_multivalue(self):
        self.dump_load(ans='1', zwo='2')
