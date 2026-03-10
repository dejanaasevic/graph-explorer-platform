import uuid
from typing import Dict, Any, Optional, List, Iterable

class Node:
    """Represent a single node in a graph.
       Each node has a unique identifier and a dictionary of key-value attributes.
    """

    def __init__(self):
        """Initialize a Node with a new UUID and an empty attribute dict."""
        self.id: uuid.UUID = uuid.uuid4()
        self.attributes: Dict[str, Any] = {}

    def add_attribute(self, attribute: str, value: Any) -> None:
        """Add or overwrite a single attribute on the node.

        Keyword arguments:
        attribute -- the attribute name (stored in lowercase)
        value     -- the value to associate with the attribute
        """
        self.attributes[attribute.lower()] = value

    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """Add or overwrite multiple attributes at once.

        Keyword arguments:
        attributes -- a dict of attribute names (stored in lowercase) to values
        """
        for key, value in attributes.items():
            self.attributes[key.lower()] = value

    def copy(self, keep_id: bool = False) -> "Node":
        """Return a new Node that is a shallow copy of this one.

        Keyword arguments:
        keep_id -- if True the copy shares this node's UUID;
                   if False (default) the copy receives a new UUID
        """
        new_node = Node()
        if keep_id:
            new_node.id = self.id
        new_node.set_attributes(self.attributes)
        return new_node

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the node."""
        return f"Node(id={self.id}, attributes={self.attributes})"


class Edge:
    """Represent a directed connection between two nodes in a graph.

    Each edge has a unique identifier, a source node, a target node,
    and a dictionary of arbitrary key-value attributes.
    """

    def __init__(self, source: Node, target: Node):
        """Initialize an Edge between two existing nodes.

        Keyword arguments:
        source -- the node where the edge originates
        target -- the node where the edge terminates
        """
        self.id: uuid.UUID = uuid.uuid4()
        self.source: Node = source
        self.target: Node = target
        self.attributes: Dict[str, Any] = {}

    def add_attribute(self, attribute: str, value: Any) -> None:
        """Add or overwrite a single attribute on the edge.

        Keyword arguments:
        attribute -- the attribute name (stored in lowercase)
        value     -- the value to associate with the attribute
        """
        self.attributes[attribute.lower()] = value

    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """Add or overwrite multiple attributes at once.

        Keyword arguments:
        attributes -- a dict of attribute names (stored in lowercase) to values
        """
        for key, value in attributes.items():
            self.attributes[key.lower()] = value

    def copy(self, new_source: Node, new_target: Node, keep_id: bool = False) -> "Edge":
        """Return a new Edge that is a shallow copy of this one.

        Keyword arguments:
        new_source -- the source node for the copied edge
        new_target -- the target node for the copied edge
        keep_id    -- if True the copy shares this edge's UUID;
                      if False (default) the copy receives a new UUID
        """
        new_edge = Edge(new_source, new_target)
        if keep_id:
            new_edge.id = self.id
        new_edge.set_attributes(self.attributes)
        return new_edge

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the edge."""
        return f"Edge({self.source.id} --> {self.target.id} attributes={self.attributes})"


class Graph:
    """Represent a graph composed of nodes and edges.

    Supports both directed and undirected graphs. Internally maintains
    an adjacency list for efficient neighbor look-ups.
    """

    def __init__(self, directed: bool):
        """Initialize an empty graph.

        Keyword arguments:
        directed -- if True edges have a direction (source → target);
                    if False edges are bidirectional
        """
        self._directed: bool = directed
        self._nodes: Dict[uuid.UUID, Node] = {}
        self._edges: Dict[uuid.UUID, Edge] = {}
        self._adjacency: Dict[uuid.UUID, List[Edge]] = {}

    def is_directed(self) -> bool:
        """Return True if the graph is directed, False otherwise."""
        return self._directed

    def get_node(self, node_id: uuid.UUID) -> Optional[Node]:
        """Return the node with the given UUID, or None if not found.

        Keyword arguments:
        node_id -- the UUID of the node to retrieve
        """
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: uuid.UUID) -> Optional[Edge]:
        """Return the edge with the given UUID, or None if not found.

        Keyword arguments:
        edge_id -- the UUID of the edge to retrieve
        """
        return self._edges.get(edge_id)

    def get_edge_between(self, source_id: uuid.UUID, target_id: uuid.UUID) -> Optional[Edge]:
        """Return the edge connecting two nodes, or None if no such edge exists.

        For undirected graphs the direction of the edge is ignored.

        Keyword arguments:
        source_id -- the UUID of the source node
        target_id -- the UUID of the target node
        """
        for edge in self._edges.values():
            if edge.source.id == source_id and edge.target.id == target_id:
                return edge
            if not self._directed and edge.source.id == target_id and edge.target.id == source_id:
                return edge
        return None

    def get_nodes(self) -> Iterable[Node]:
        """Return an iterable of all nodes in the graph."""
        return self._nodes.values()

    def get_edges(self) -> Iterable[Edge]:
        """Return an iterable of all edges in the graph."""
        return self._edges.values()

    def add_node(self, node: Node) -> None:
        """Add a node to the graph if it is not already present.

        Keyword arguments:
        node -- the Node instance to add
        """
        if node.id not in self._nodes:
            self._nodes[node.id] = node
            self._adjacency[node.id] = []

    def can_add_edge(self, edge: Edge) -> bool:
        """Return True if the edge can be added to the graph, False otherwise.

        An edge cannot be added if:
        - an edge with the same UUID already exists
        - either endpoint node is not in the graph
        - the graph is undirected and a parallel edge already exists

        Keyword arguments:
        edge -- the Edge instance to check
        """
        if edge.id in self._edges:
            return False
        elif edge.source.id not in self._nodes or edge.target.id not in self._nodes:
            return False
        if not self._directed:
            opposite_edge = self.get_edge_between(edge.target.id, edge.source.id)
            if opposite_edge:
                return False
        return True

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph if it passes the can_add_edge check.

        For undirected graphs the edge is registered in the adjacency
        lists of both endpoint nodes.

        Keyword arguments:
        edge -- the Edge instance to add
        """
        if self.can_add_edge(edge):
            self._edges[edge.id] = edge
            self._adjacency[edge.source.id].append(edge)
            if not self._directed:
                self._adjacency[edge.target.id].append(edge)

    def remove_node(self, node_id: uuid.UUID) -> None:
        """Remove a node and all edges connected to it from the graph.

        Does nothing if the node is not present.

        Keyword arguments:
        node_id -- the UUID of the node to remove
        """
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

    def remove_edge(self, edge_id: uuid.UUID) -> None:
        """Remove an edge from the graph by its UUID.

        Does nothing if the edge is not present. For undirected graphs
        the edge is removed from the adjacency lists of both endpoints.

        Keyword arguments:
        edge_id -- the UUID of the edge to remove
        """
        edge_to_remove = self._edges.pop(edge_id, None)
        if edge_to_remove:
            self._adjacency[edge_to_remove.source.id].remove(edge_to_remove)
            if not self._directed:
                self._adjacency[edge_to_remove.target.id].remove(edge_to_remove)

    def get_neighbors(self, node_id: uuid.UUID) -> List[Node]:
        """Return a list of nodes directly reachable from the given node.

        For directed graphs only outgoing edges are considered.
        For undirected graphs both endpoints of each adjacent edge are checked.

        Keyword arguments:
        node_id -- the UUID of the node whose neighbors are requested
        """
        neighbors = []
        for edge in self._adjacency[node_id]:
            if self._directed or edge.source.id == node_id:
                neighbors.append(edge.target)
            else:
                neighbors.append(edge.source)
        return neighbors

    def __repr__(self) -> str:
        """Return a human-readable summary of the graph including all nodes and edges."""
        graph_str = f"Graph(nodes={len(self._nodes)}, edges={len(self._edges)}, directed={self._directed})\n"
        graph_str += "Nodes: \n"
        for node in self._nodes.values():
            graph_str += f"{node}\n"
        graph_str += "Edges: \n"
        for edge in self._edges.values():
            graph_str += f"{edge}\n"
        return graph_str