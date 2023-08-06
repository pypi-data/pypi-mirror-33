"""
Node persistence.

"""
from microcosm_propertygraph.stores.base import NaiveStore, Store
from microcosm_propertygraph.models.node import Node


class NodeStore(Store):
    """
    Read-only access to the collection of all nodes.

    """
    def __init__(self, graph=None, model_class=Node):
        super().__init__(graph, model_class)


class NaiveNodeStore(NaiveStore, NodeStore):
    """
    Node store implementation using a single iterator.

    """
    pass
