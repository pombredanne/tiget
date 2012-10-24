from tiget.git import auto_transaction, get_transaction, GitError


class Manager(object):
    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)
        self.model = cls

    @auto_transaction()
    def _fetch(self, pk):
        instance = self.model(pk=pk)
        try:
            content = get_transaction().get_blob(instance.path).decode('utf-8')
        except GitError:
            raise self.model.DoesNotExist()
        instance.loads(content)
        return instance

    @auto_transaction()
    def all(self):
        instances = []
        for pk in get_transaction().list_blobs([self.model._meta.storage_name]):
            pk = self.model._meta.pk.loads(pk)
            instances += [self._fetch(pk)]
        return instances

    def get(self, **kwargs):
        objs = self.filter(**kwargs)
        if len(objs) == 1:
            return objs[0]
        elif not objs:
            raise self.model.DoesNotExist()
        else:
            raise self.model.MultipleObjectsReturned()

    def filter(self, **kwargs):
        if 'pk' in kwargs:
            kwargs[self.model._meta.pk.attname] = kwargs.pop('pk')
        pk = kwargs.pop(self.model._meta.pk.attname, None)
        if not pk is None:
            pk = self.model._meta.pk.loads(pk)
            try:
                objs = [self._fetch(pk)]
            except self.model.DoesNotExist:
                objs = []
        else:
            objs = self.all()
        filtered = []
        # TODO: use incidces for filtering
        for obj in objs:
            if all(getattr(obj, k) == v for k, v in kwargs.items()):
                filtered += [obj]
        return filtered

    def exists(self, **kwargs):
        return bool(self.filter(**kwargs))

    def count(self, **kwargs):
        return len(self.filter(**kwargs))

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj
