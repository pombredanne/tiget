import re
import textwrap

__all__ = ['dumps', 'loads']

ITEM_SEPARATOR = re.compile(r'\n(?!\s)')
ITEM_MATCHER = re.compile(
    r'(?P<key>\w+):\s?(?P<value>.*?)$(?P<value2>.+)?', re.MULTILINE | re.DOTALL)


def dumps(data):
    s = u''
    for k, v in data.iteritems():
        value = v or u''
        s += u'{}: {}\n'.format(k, value.replace(u'\n', u'\n    '))
    return s


def loads(s):
    data = {}
    lineno = 0
    for item in ITEM_SEPARATOR.split(s):
        if not item.startswith(u'#') and item.strip():
            m = ITEM_MATCHER.match(item)
            if not m:
                raise ValueError(
                    'syntax error on line {}'.format(lineno + 1))
            value = m.group('value')
            value += textwrap.dedent(m.group('value2') or u'')
            data[m.group('key')] = value or None
        lineno += item.count(u'\n') + 1
    return data
