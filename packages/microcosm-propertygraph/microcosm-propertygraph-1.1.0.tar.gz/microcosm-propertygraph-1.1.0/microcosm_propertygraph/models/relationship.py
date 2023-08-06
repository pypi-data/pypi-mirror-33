"""
Relationship pseudo-model.

"""


class Relationship:

    def __init__(self, start_id, end_id, type, properties):
        """
        A relationship (edge) in a property graph view of data.

        :param {str} start_id: unique id of the 'from' node in the graph this relationship is associated with
        :param {str} end_id: unique id of the 'to' node in the graph this relationship is associated with
        :param {list} type: a qualified relationship 'type' to use, typically corresponding to some enumeration
        :param {dict} properties: any scalar attributes ("properties") associated with the relationship.

        """
        self.start_id = start_id
        self.end_id = end_id
        self.type = type
        self.properties = properties
