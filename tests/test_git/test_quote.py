import unittest

from tiget.git.quote import quote_filename, unquote_filename


class TestQuote(unittest.TestCase):
    def test_quote_unquote(self):
        testnames = [
            'foo',
            'foo\nbar',
            '!@#$%^&*()_+-[]\'\"|',
        ]
        for name in testnames:
            self.assertEqual(unquote_filename(quote_filename(name)), name)
