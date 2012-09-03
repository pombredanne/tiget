from nose.tools import ok_, eq_, raises

from tiget.utils import serializer


class TestSerializer(object):
    def test_loads_none(self):
        data = serializer.loads(u'none: ')
        eq_(len(data), 1)
        eq_(data['none'], None)

    def test_loads_oneline(self):
        data = serializer.loads(u'oneline: foo')
        eq_(len(data), 1)
        eq_(data['oneline'], u'foo')

    def test_loads_multiline(self):
        data = serializer.loads(u'multiline: foo\n    bar\n    baz')
        eq_(len(data), 1)
        eq_(data['multiline'], u'foo\nbar\nbaz')

    def test_loads_comment(self):
        data = serializer.loads(u'# foo')
        eq_(len(data), 0)

    def test_loads_multiline_comment(self):
        data = serializer.loads(u'# foo\n    bar\n    baz')
        eq_(len(data), 0)

    def test_loads_blankline(self):
        data = serializer.loads(u'')
        eq_(len(data), 0)

    def test_loads_blankline_with_space(self):
        data = serializer.loads(u' ')
        eq_(len(data), 0)

    @raises(ValueError)
    def test_loads_broken(self):
        data = serializer.loads(u'I am broken')

    def test_dumps_none(self):
        s = serializer.dumps({'none': None})
        eq_(s, 'none: \n')

    def test_dumps_oneline(self):
        s = serializer.dumps({'oneline': 'foo'})
        eq_(s, 'oneline: foo\n')

    def test_dumps_multiline(self):
        s = serializer.dumps({'multiline': 'foo\nbar\nbaz'})
        eq_(s, 'multiline: foo\n    bar\n    baz\n')
