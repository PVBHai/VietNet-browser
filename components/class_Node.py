class Node:
    def __init__(self, synset, recursive_level=0):
        self._synset = synset
        # self._lemmas = ', '.join(lemma.name() for lemma in synset.lemmas())
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
