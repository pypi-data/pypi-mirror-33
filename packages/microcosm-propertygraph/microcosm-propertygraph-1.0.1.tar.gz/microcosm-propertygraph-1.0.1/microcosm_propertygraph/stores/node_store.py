"""
Node store.

"""
from abc import ABCMeta, abstractmethod
from itertools import islice

from microcosm_postgres.store import Store
from microcosm_propertygraph.models.node import Node


class NodeStoreBase(Store, metaclass=ABCMeta):

    def __init__(self, graph, model_class=Node):
        super(NodeStoreBase, self).__init__(graph, model_class)

    def count(self, **kwargs):
        return sum(1 for n in self.iter_nodes(**kwargs))

    def search(self, offset, limit, **kwargs):
        return islice(
            self.iter_nodes(**kwargs),
            offset,
            limit,
        )

    @abstractmethod
    def iter_nodes(self, **kwargs):
        """
        Iterate over `Node` instances. Derived classes will need to implement logic here
        to materialize data required and yield Node instances.

        """
