from tiget.git.models.queryset import QuerySet


class Manager(object):
    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)
        self.model = cls

    def filter(self, **kwargs):
        return QuerySet(self.model).filter(**kwargs)

    def all(self):
        return self.filter()

    def get(self, **kwargs):
        return self.filter(**kwargs).get()

    def exists(self, **kwargs):
        return self.filter(**kwargs).exists()

    def count(self, **kwargs):
        return self.filter(**kwargs).count()

    def order_by(self, *order_by):
        return self.all().order_by(*order_by)

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj
