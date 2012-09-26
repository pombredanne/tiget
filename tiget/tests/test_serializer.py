from nose.tools import ok_, eq_, raises

from tiget.serializer import dumps, loads


class TestSerializer(object):
    def test_loads_none(self):
        data = loads(u'none: ')
        eq_(len(data), 1)
        eq_(data['none'], None)

    def test_loads_oneline(self):
        data = loads(u'oneline: foo')
        eq_(len(data), 1)
        eq_(data['oneline'], u'foo')

    def test_loads_multiline(self):
        data = loads(u'multiline: foo\n    bar\n    baz')
        eq_(len(data), 1)
        eq_(data['multiline'], u'foo\nbar\nbaz')

    def test_loads_comment(self):
        data = loads(u'# foo')
        eq_(len(data), 0)

    def test_loads_multiline_comment(self):
        data = loads(u'# foo\n    bar\n    baz')
        eq_(len(data), 0)

    def test_loads_blankline(self):
        data = loads(u'')
        eq_(len(data), 0)

    def test_loads_blankline_with_space(self):
        data = loads(u' ')
        eq_(len(data), 0)

    @raises(ValueError)
    def test_loads_broken(self):
        data = loads(u'I am broken')

    def test_dumps_none(self):
        s = dumps({'none': None})
        eq_(s, 'none: \n')

    def test_dumps_oneline(self):
        s = dumps({'oneline': 'foo'})
        eq_(s, 'oneline: foo\n')

    def test_dumps_multiline(self):
        s = dumps({'multiline': 'foo\nbar\nbaz'})
        eq_(s, 'multiline: foo\n    bar\n    baz\n')
