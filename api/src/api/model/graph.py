import uuid
from typing import Dict, Any, Optional, List


class Node:
    def __init__(self, attributes: Dict[str, Any] = None ):
        self.node_id : uuid.UUID = uuid.uuid4()
        self.attributes : Dict[str, Any] = attributes or {}

    def __repr__(self):
        return f"Node(id={self.node_id}, attributes={self.attributes})"

class Edge:
    def __init__(self, source : Node, target : Node, attributes: Dict[str, Any] = None):
        self.id : uuid.UUID = uuid.uuid4()
        self.source : Node = source
        self.target : Node = target
        self.attributes: Dict[str, Any] = attributes or {}

    def __repr__(self):
        return f"Edge({self.source.node_id} --> {self.target.node_id})"

class Graph:
    def __init__(self, directed : bool):
        self.directed : bool = directed
        self._nodes : Dict[uuid.UUID, Node] = {}
        self._edges : Dict[uuid.UUID, Edge] = {}
        self._adjacency: Dict[uuid.UUID, List[Edge]] = {}

    def get_node(self, node_id: uuid.UUID) -> Optional[Node]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: uuid.UUID) -> Optional[Edge]:
        return self._edges.get(edge_id)

    def get_edge(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Optional[Edge]:
        for edge in self._edges.values():
            if edge.source.node_id == source_id and edge.target.node_id == target_id:
                return edge
            if not self.directed and edge.source.node_id == target_id and edge.target.node_id == source_id:
                return edge
        return None

    def get_nodes(self) -> Iterable[Node]:
        return self._nodes.values()

    def get_edges(self) -> Iterable[Edge]:
        return self._edges.values()

    def add_node(self, node : Node) -> None:
        if node.node_id not in self._nodes:
            self._nodes[node.node_id] = node
            self._adjacency[node.node_id] = []

    def can_add_edge(self, edge: Edge) -> bool:
        if edge.id in self._edges:
            return False
        elif edge.source.node_id not in self._nodes or edge.target.node_id not in self._nodes:
            return False
        if not self.directed:
            opposite_edge = self.get_edge(edge.target.node_id,edge.source.node_id)
            if opposite_edge:
                return False
        return True

    def add_edge(self, edge : Edge) -> None:
        if self.can_add_edge(edge):
            self._edges[edge.id] = edge
            self._adjacency[edge.source.node_id].append(edge)
            if not self.directed:
                self._adjacency[edge.target.node_id].append(edge)

    def remove_node(self, node_id : uuid.UUID) -> None:
        if node_id not in self._nodes:
            return
        edges_to_remove = []
        for edge in self._edges.values():
            if edge.source.node_id == node_id or edge.target.node_id == node_id:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            self.remove_edge(edge.id)

        self._adjacency.pop(node_id, None)
        self._nodes.pop(node_id)

    def remove_edge(self, edge_id : uuid.UUID) -> None:
        edge = self._edges.pop(edge_id, None)
        if edge:
            self._adjacency[edge.source.node_id].remove(edge)
            if not self.directed:
                self._adjacency[edge.target.node_id].remove(edge)


    def get_neighbors(self, node_id : uuid.UUID) -> List[Node]:
        neighbors = []
        for edge in self._adjacency[node_id]:
            if self.directed or edge.source.node_id == node_id:
                neighbors.append(edge.target)
            else:
                neighbors.append(edge.source)
        return neighbors

    def __repr__(self):
        return f"Graph(nodes={len(self._nodes)}, edges={len(self._edges)}, directed={self.directed})"