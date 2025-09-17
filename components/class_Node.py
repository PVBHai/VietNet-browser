from components.utils_search import get_viet_info_from_synset

class Node:
    def __init__(self, synset, folder_path, recursive_level=0):
        search_result = get_viet_info_from_synset(synset.id, folder_path)

        self._synset = synset
        self._viet_lemmas = search_result['viet_word']
        self._viet_definition = search_result['viet_definition']
        self._viet_example = search_result['viet_example']
        self._is_same = search_result['is_same']
        self._lemmas = ', '.join(lemma for lemma in synset.lemmas())
        self._definition = synset.definition()
        self._example = synset.examples()
        self._level = recursive_level
        self._children = []

    @property
    def children(self):
        return self._children
    
    @children.setter
    def children(self, value):
        self._children = value
