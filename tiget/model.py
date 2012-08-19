import re, textwrap
from collections import OrderedDict
from uuid import uuid4
from tiget.git import need_transaction

class Field(object):
    creation_counter = 0

    def __init__(self, default=None, hidden=False):
        self._default = default
        self.hidden = hidden
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    @property
    def default(self):
        default = self._default
        if hasattr(default, '__call__'):
            default = default()
        return default

class TextField(Field):
    pass

class ModelBase(type):
    def __new__(cls, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if parents:
            fields = []
            for k, v in attrs.items():
                if isinstance(v, Field):
                    fields += [(k, v)]
                    del attrs[k]
            fields.sort(key=lambda x: x[1].creation_counter)
            fields = OrderedDict(fields)
            if not 'id' in fields:
                fields['id'] = TextField(default=lambda: uuid4().hex, hidden=True)
            attrs['fields'] = fields
        return super(ModelBase, cls).__new__(cls, name, bases, attrs)

class Model(object):
    __metaclass__ = ModelBase

    def __init__(self, **kwargs):
        self.data = {}
        for k, v in kwargs.iteritems():
            if not k in self.fields.keys():
                raise Exception('field "{0}" does not exist'.format(k))
            self.data[k] = v
            transaction.add_message(u'Initialize Repository')

    def __getattr__(self, name):
        field = self.fields.get(name, None)
        if field:
            return self.data.get(name, field.default)
        raise AttributeError

    def __setattr__(self, name, value):
        if name in self.fields:
            self.data[name] = value
        else:
            super(Model, self).__setattr__(name, value)

    def serialize(self, include_hidden=False):
        content = OrderedDict()
        for name, field in self.fields.iteritems():
            if not include_hidden and field.hidden:
                continue
            content[name] = self.data.get(name, field.default)
        s = u''
        for k, v in content.iteritems():
            value = v or u''
            s += u'{0}: {1}\n'.format(k, value.replace(u'\n', u'\n    '))
        return s

    def deserialize(self, s):
        lines = []
        backlog = None
        def _flush():
            if backlog:
                line = backlog[0]
                if len(backlog) > 1:
                    line += u'\n' + textwrap.dedent(u'\n'.join(backlog[1:]))
                lines.append(line)
        for line in s.splitlines():
            if line.startswith(u' ') or not line:
                if not backlog:
                    raise Exception('syntax error')
                backlog += [line]
            else:
                _flush()
                backlog = [line]
        _flush()
        for line in lines:
            if line.startswith(u'#'):
                continue
            m = re.match(r'\A(\w+):\s?(.*)\Z', line, re.MULTILINE | re.DOTALL)
            if m:
                name = m.group(1)
                value = m.group(2)
                self.data[name] = value
            else:
                raise Exception('syntax error')

    def save(self):
        with need_transaction() as transaction:
            if not transaction.is_initialized:
                raise Exception('git repository is not initialized')
            pluralized = self.__class__.__name__.lower() + 's'
            transaction.add_file('{0}/{1}'.format(pluralized, self.id), self.serialize(include_hidden=True))
            # TODO: better commit message
            transaction.add_message(u'Edit ticket {0}'.format(self.id))

    @classmethod
    def get(instance_id):
        raise NotImplementedError

    @classmethod
    def all():
        raise NotImplementedError
