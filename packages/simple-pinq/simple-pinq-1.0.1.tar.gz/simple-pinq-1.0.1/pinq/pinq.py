__all__ = ['Pinq']


class Pinq:
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return iter(self.iterable)

    def select(self, func):
        return Pinq(map(func, self.iterable))

    def where(self, predicate):
        return Pinq(filter(predicate, self.iterable))

    def to_list(self):
        return list(self)

    def to_set(self):
        return set(self)

    def sum(self):
        return sum(self)

    def min(self):
        return min(self)

    def max(self):
        return max(self)

    @staticmethod
    def attr(attr_name):
        def func(obj):
            return getattr(obj, attr_name)
        return func

    @staticmethod
    def item(item_name):
        def func(obj):
            return obj[item_name]
        return func
