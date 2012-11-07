import unittest

from tiget.serializer import dumps, loads


class TestSerializerDump(unittest.TestCase):
    def test_dumps_none(self):
        s = dumps({'none': None})
        self.assertEqual(s, 'none: \n')

    def test_dumps_oneline(self):
        s = dumps({'oneline': 'foo'})
        self.assertEqual(s, 'oneline: foo\n')

    def test_dumps_multiline(self):
        s = dumps({'multiline': 'foo\nbar\nbaz'})
        self.assertEqual(s, 'multiline: foo\n    bar\n    baz\n')


class TestSerializerLoad(unittest.TestCase):
    def test_loads_none(self):
        data = loads('none: ')
        self.assertEqual(len(data), 1)
        self.assertEqual(data['none'], None)

    def test_loads_oneline(self):
        data = loads('oneline: foo')
        self.assertEqual(len(data), 1)
        self.assertEqual(data['oneline'], 'foo')

    def test_loads_multiline(self):
        data = loads('multiline: foo\n    bar\n    baz')
        self.assertEqual(len(data), 1)
        self.assertEqual(data['multiline'], 'foo\nbar\nbaz')

    def test_loads_comment(self):
        data = loads('# foo')
        self.assertEqual(len(data), 0)

    def test_loads_multiline_comment(self):
        data = loads('# foo\n    bar\n    baz')
        self.assertEqual(len(data), 0)

    def test_loads_blankline(self):
        data = loads('')
        self.assertEqual(len(data), 0)

    def test_loads_blankline_with_space(self):
        data = loads(' ')
        self.assertEqual(len(data), 0)

    def test_loads_broken(self):
        self.assertRaises(ValueError, loads, 'b0rked')


class TestSerializerDumpLoad(unittest.TestCase):
    def dump_load(self, **data):
        s = dumps(data)
        restored = loads(s)
        self.assertEqual(len(data), len(restored))
        self.assertEqual(data.keys(), restored.keys())
        for key in data.keys():
            self.assertEqual(data[key], restored[key])

    def test_none(self):
        self.dump_load(nada=None)

    def test_oneline(self):
        self.dump_load(oneline='foo')

    def test_multiline(self):
        self.dump_load(multiline='foo\nbar\nbaz')

    def test_multivalue(self):
        self.dump_load(ans='1', zwo='2')
