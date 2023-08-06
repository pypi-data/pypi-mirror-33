"""
Relationship store.

"""
from microcosm_propertygraph.stores.base import NaiveStore, Store
from microcosm_propertygraph.models.relationship import Relationship


class RelationshipStore(Store):
    """
    Read-only access to the collection of all relationships.

    """
    def __init__(self, graph=None, model_class=Relationship):
        super().__init__(graph, model_class)


class NaiveRelationshipStore(NaiveStore, RelationshipStore):
    """
    Relationship store implementation using a single iterator.

    """
    pass
