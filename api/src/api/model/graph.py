import uuid
from typing import Dict, Any, Optional, List, Iterable

class Node:
    def __init__(self):
        self.id : uuid.UUID = uuid.uuid4()
        self.attributes : Dict[str, Any] =  {}

    def add_attribute(self, attribute : str, value : Any) -> None:
        self.attributes[attribute.lower()] = value

    def set_attributes(self, attributes : Dict[str, Any]):
        for key, value in attributes.items():
            self.attributes[key.lower()] = value

    def copy(self, keep_id: bool = False) -> "Node":
        new_node = Node()
        if keep_id:
            new_node.id = self.id
        new_node.set_attributes(self.attributes)
        return new_node

    def __repr__(self):
        return f"Node(id={self.id}, attributes={self.attributes})"

class Edge:
    def __init__(self, source : Node, target : Node):
        self.id : uuid.UUID = uuid.uuid4()
        self.source : Node = source
        self.target : Node = target
        self.attributes: Dict[str, Any] = {}

    def add_attribute(self, attribute : str, value : Any) -> None:
        self.attributes[attribute.lower()] = value

    def set_attributes(self, attributes : Dict[str, Any]):
        for key, value in attributes.items():
            self.attributes[key.lower()] = value

    def copy(self, new_source: Node, new_target: Node, keep_id: bool = False) -> "Edge":
        new_edge = Edge(new_source, new_target)
        if keep_id:
            new_edge.id = self.id
        new_edge.set_attributes(self.attributes)
        return new_edge

    def __repr__(self):
        return f"Edge({self.source.id} --> {self.target.id} attributes={self.attributes})"

class Graph:
    def __init__(self, directed : bool):
        self._directed : bool = directed
        self._nodes : Dict[uuid.UUID, Node] = {}
        self._edges : Dict[uuid.UUID, Edge] = {}
        self._adjacency: Dict[uuid.UUID, List[Edge]] = {}

    def is_directed(self) -> bool:
        return self._directed

    def get_node(self, node_id: uuid.UUID) -> Optional[Node]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: uuid.UUID) -> Optional[Edge]:
        return self._edges.get(edge_id)

    def get_edge_between(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Optional[Edge]:
        for edge in self._edges.values():
            if edge.source.id == source_id and edge.target.id == target_id:
                return edge
            if not self._directed and edge.source.id == target_id and edge.target.id == source_id:
                return edge
        return None

    def get_nodes(self) -> Iterable[Node]:
        return self._nodes.values()

    def get_edges(self) -> Iterable[Edge]:
        return self._edges.values()

    def add_node(self, node : Node) -> None:
        if node.id not in self._nodes:
            self._nodes[node.id] = node
            self._adjacency[node.id] = []

    def can_add_edge(self, edge: Edge) -> bool:
        if edge.id in self._edges:
            return False
        elif edge.source.id not in self._nodes or edge.target.id not in self._nodes:
            return False
        if not self._directed:
            opposite_edge = self.get_edge_between(edge.target.id, edge.source.id)
            if opposite_edge:
                return False
        return True

    def add_edge(self, edge : Edge) -> None:
        if self.can_add_edge(edge):
            self._edges[edge.id] = edge
            self._adjacency[edge.source.id].append(edge)
            if not self._directed:
                self._adjacency[edge.target.id].append(edge)

    def remove_node(self, node_id : uuid.UUID) -> None:
        if node_id not in self._nodes:
            return
        edges_to_remove = []
        for edge in self._edges.values():
            if edge.source.id == node_id or edge.target.id == node_id:
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            self.remove_edge(edge.id)
        self._adjacency.pop(node_id, None)
        self._nodes.pop(node_id)

    def remove_edge(self, edge_id : uuid.UUID) -> None:
        edge_to_remove = self._edges.pop(edge_id, None)
        if edge_to_remove:
            self._adjacency[edge_to_remove.source.id].remove(edge_to_remove)
            if not self._directed:
                self._adjacency[edge_to_remove.target.id].remove(edge_to_remove)

    def get_neighbors(self, node_id : uuid.UUID) -> List[Node]:
        neighbors = []
        for edge in self._adjacency[node_id]:
            if self._directed or edge.source.id == node_id:
                neighbors.append(edge.target)
            else:
                neighbors.append(edge.source)
        return neighbors

    def __repr__(self):
        graph_str =  f"Graph(nodes={len(self._nodes)}, edges={len(self._edges)}, directed={self._directed})\n"
        graph_str += f"Nodes: \n"
        for node in self._nodes.values():
            graph_str += f"{node}\n"
        graph_str += f"Edges: \n"
        for edge in self._edges.values():
            graph_str += f"{edge}\n"
        return graph_str
