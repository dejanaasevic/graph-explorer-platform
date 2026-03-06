import uuid

from api.model import Graph, Edge, Node

# ───────────────── Helpers ─────────────────

def make_graph(directed = True):
    graph = Graph(directed=directed)

    first_node, second_node = Node(), Node()
    graph.add_node(first_node)
    graph.add_node(second_node)

    edge = Edge(first_node, second_node)
    graph.add_edge(edge)
    return graph, first_node, second_node, edge

# ───────────────── Node ─────────────────

class TestNode:
    def test_unique_ids(self):
        assert Node().id != Node().id

    def test_add_attribute_lowercase(self):
        node = Node()
        node.add_attribute("Name", "Alice")
        assert "name" in node.attributes
        assert node.attributes["name"] == "Alice"

    def test_set_attributes_multiple(self):
        node = Node()
        node.set_attributes({"Age": 24, "City": "New York"})
        assert node.attributes["age"] == 24
        assert node.attributes["city"] == "New York"

    def test_copy_new_id_by_default(self):
        node = Node()
        node.add_attribute("Name", "Alice")
        copy_node = node.copy()
        assert copy_node.id != node.id
        assert copy_node.attributes == node.attributes

    def test_copy_keep_id(self):
        node = Node()
        copy_node = node.copy(keep_id=True)
        assert copy_node.id == node.id

    def test_copy_is_shallow(self):
        node = Node()
        node.add_attribute("Name", "Alice")
        copy_node = node.copy()
        copy_node.add_attribute("Name", "Bod")
        assert node.attributes["name"] == "Alice"

    def test_repr_contains_id(self):
        node = Node()
        assert str(node.id) in repr(node)

# ───────────────── Edge ─────────────────

class TestEdge:
    def test_source_and_target(self):
        first_node, second_node = Node(), Node()
        edge = Edge(first_node, second_node)
        assert edge.source is first_node
        assert edge.target is second_node

    def test_unique_ids(self):
        first_node, second_node = Node(), Node()
        assert Edge(first_node, second_node).id != Edge(second_node, first_node).id

    def test_add_attribute_lowercase(self):
        first_node, second_node = Node(), Node()
        edge = Edge(first_node, second_node)
        edge.add_attribute("Name", "Alice")
        assert edge.attributes["name"] == "Alice"

    def test_copy_new_nodes(self):
        first_node, second_node, third_node, fourth_node = Node(), Node(), Node(), Node()
        edge = Edge(first_node, second_node)
        edge.add_attribute("Name", "Alice")
        copy_edge = edge.copy(third_node, fourth_node)
        assert copy_edge.source is third_node
        assert copy_edge.target is fourth_node
        assert copy_edge.attributes["name"] == "Alice"
        assert copy_edge.id != edge.id

    def test_copy_keep_id(self):
        first_node, second_node, third_node, fourth_node = Node(), Node(), Node(), Node()
        edge = Edge(first_node, second_node)
        copy_edge = edge.copy(third_node, fourth_node, keep_id=True)
        assert  copy_edge.id == edge.id

    def test_repr_shows_arrow(self):
        first_node, second_node = Node(), Node()
        edge = Edge(first_node, second_node)
        assert "-->" in repr(edge)

# ───────────────── Graph – directed ─────────────────

class TestDirectedGraph:
    def test_is_directed(self):
        assert Graph(directed=True).is_directed() is True

    def test_add_and_get_node(self):
        graph = Graph(directed=True)
        node = Node()
        graph.add_node(node)
        assert graph.get_node(node.id) is node

    def test_add_node_twice_is_idempotent(self):
        graph = Graph(directed=True)
        node = Node()
        graph.add_node(node)
        graph.add_node(node)
        assert len(list(graph.get_nodes())) == 1

    def test_add_and_get_edge(self):
        graph, first_node, second_node, edge = make_graph(directed=True)
        assert graph.get_edge(edge.id) is edge

    def test_cannot_add_edge_unknown_node(self):
        graph = Graph(directed=True)
        first_node, second_node = Node(), Node()
        graph.add_node(first_node)
        edge = Edge(first_node, second_node)
        assert graph.can_add_edge(edge) is False

    def test_cannot_add_duplicate_edge_id(self):
        graph, first_node, second_node, edge = make_graph(directed=True)
        assert graph.can_add_edge(edge) is False

    def test_get_edge_between(self):
        graph, first_node, second_node, edge = make_graph(directed=True)
        assert graph.get_edge_between(first_node.id, second_node.id) is edge
        assert graph.get_edge_between(second_node.id, first_node.id) is None

    def test_neighbors_directed(self):
        graph, first_node, second_node, _ = make_graph(directed=True)
        assert graph.get_neighbors(first_node.id) == [second_node]
        assert graph.get_neighbors(second_node.id) == []

    def test_remove_node_also_removes_edges(self):
        graph, first_node, second_node, edge = make_graph(directed=True)
        graph.remove_node(first_node.id)
        assert graph.get_node(first_node.id) is None
        assert graph.get_edge(edge.id) is None

    def test_remove_nonexistent_node_is_safe(self):
        graph = Graph(directed=True)
        graph.remove_node(uuid.uuid4())

    def test_remove_edge(self):
        graph, first_node, second_node, edge = make_graph(directed=True)
        graph.remove_edge(edge.id)
        assert graph.get_edge(edge.id) is None

    def test_remove_nonexistent_edge_is_safe(self):
        graph = Graph(directed=True)
        graph.remove_edge(uuid.uuid4())

    def test_repr_contains_counts(self):
        graph, *_ = make_graph(directed=True)
        r = repr(graph)
        assert "nodes=2" in r
        assert "edges=1" in r

# ───────────────── Graph – undirected ─────────────────

class TestUndirectedGraph:
    def test_is_not_directed(self):
        assert Graph(directed=False).is_directed() is False

    def test_neighbors_both_directions(self):
        graph, first_node, second_node, _ = make_graph(directed=False)
        assert second_node in graph.get_neighbors(first_node.id)
        assert first_node in graph.get_neighbors(second_node.id)

    def test_no_parallel_edge_undirected(self):
        graph = Graph(directed=False)
        first_node, second_node = Node(), Node()
        graph.add_node(first_node)
        graph.add_node(second_node)
        first_edge = Edge(first_node, second_node)
        second_edge = Edge(second_node, first_node)
        graph.add_edge(first_edge)
        assert graph.can_add_edge(second_edge) is False

    def test_get_edge_between_ignores_direction(self):
        graph, first_node, second_node, edge = make_graph(directed=False)
        assert graph.get_edge_between(second_node.id, first_node.id) is edge

    def test_remove_edge_updates_both_adjacency_lists(self):
        graph, first_node, second_node, edge = make_graph(directed=False)
        graph.remove_edge(edge.id)
        assert graph.get_neighbors(first_node.id) == []
        assert graph.get_neighbors(second_node.id) == []
