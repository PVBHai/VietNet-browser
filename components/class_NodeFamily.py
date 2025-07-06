from components.class_Node import *
from components.utils_wn import get_relationships


class NodeFamily:
    def __init__(self, root_synsets, relationship_type, max_recursive=1):
        self.root_synsets = root_synsets
        self.relationship_type = relationship_type
        self.max_recursive = max_recursive
        self.nodes = self._build_tree(root_synsets, 0)

    def _build_tree(self, synsets, level):
        if level >= self.max_recursive or not synsets:
            return []

        node_list = []
        for syn in synsets:
            node = Node(syn, level)
            children_synsets = get_relationships(syn, self.relationship_type)
            node.children = self._build_tree(children_synsets, level + 1)
            node_list.append(node)
        return node_list

