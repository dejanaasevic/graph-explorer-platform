from typing import List

class Graph(object):
    def __init__(self, nodes:List[object]=None, edges:List[object]=None):
        self._nodes = nodes
        self._edges = edges

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @nodes.setter
    def nodes(self, value):
        self._nodes = value

    @edges.setter
    def edges(self, value):
        self._edges = value