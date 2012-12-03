from tiget.git.models.queryset import QuerySet


class Manager:
    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)
        self.model = cls

    def all(self):
        return self.filter()

    def filter(self, *args, **kwargs):
        return QuerySet(self.model).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        return QuerySet(self.model).exclude(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.filter(*args, **kwargs).get()

    def exists(self, *args, **kwargs):
        return self.filter(*args, **kwargs).exists()

    def count(self, *args, **kwargs):
        return self.filter(*args, **kwargs).count()

    def order_by(self, *order_by):
        return self.all().order_by(*order_by)

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj
