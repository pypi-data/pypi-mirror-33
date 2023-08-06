"""
Persistence idioms.

"""
from abc import ABCMeta, abstractmethod
from itertools import islice


class Store(metaclass=ABCMeta):
    """
    Read-only access to a collection of resources.

    """
    def __init__(self, graph, model_class):
        self.model_class = model_class

    @abstractmethod
    def count(self, **kwargs):
        pass

    @abstractmethod
    def search(self, offset, limit, **kwargs):
        pass


class NaiveStore(Store):
    """
    A naive store implementation that uses a single iterator.

    """
    def count(self, **kwargs):
        return sum(1 for n in self.iter_items(**kwargs))

    def search(self, offset=0, limit=None, **kwargs):
        items = self.iter_items(**kwargs)

        if limit is None:
            return islice(items, offset, None)

        return islice(items, offset, offset + limit)

    @abstractmethod
    def iter_items(self, **kwargs):
        pass
