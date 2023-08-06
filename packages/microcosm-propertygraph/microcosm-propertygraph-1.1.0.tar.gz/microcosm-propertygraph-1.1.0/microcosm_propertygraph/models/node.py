"""
Node pseudo-model.

"""


class Node:

    def __init__(self, id, labels, properties):
        """
        A node in a property graph view of data.

        :param {str} id: unique id of the node in the graph
        :param {list} labels: one or more 'labels' which describe the node type, typically corresponding to some
            enumeration (e.g. 'SERVICE_PROVIDER')
        :param {dict} properties: any scalar attributes ("properties") associated with the node. this excludes
            specifically relationships to other nodes in the graph which are represented via the dedicated
            `Relationship` model.

        """
        self.id = id
        self.labels = labels
        self.properties = properties
