import datetime
import pytest

from api.model import Node, Edge, Graph
from use_cases.query_engine import QueryEngine
from use_cases.query_parser import FilterExpression

def make_graph() -> Graph:
    graph = Graph(directed=True)

    alice = Node()
    alice.set_attributes({"name": "Alice", "age": 30, "city": "Berlin"})

    bob = Node()
    bob.set_attributes({"name": "Bob", "age": 25, "city": "Berlin"})

    carol = Node()
    carol.set_attributes({"name": "Carol", "age": 35, "city": "Paris"})

    graph.add_node(alice)
    graph.add_node(bob)
    graph.add_node(carol)

    first_edge = Edge(alice, bob)
    first_edge.add_attribute("type", "friends")
    graph.add_edge(first_edge)

    second_edge = Edge(bob, carol)
    second_edge.add_attribute("type", "colleagues")
    graph.add_edge(second_edge)

    return graph

# ───────────────── search ─────────────────

class TestSearch:
    def test_match_by_value(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "Alice")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice"}

    def test_match_is_case_insensitive(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "alice")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice"}

    def test_match_multiple_nodes(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "Berlin")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice", "Bob"}

    def test_no_match_returns_empty_graph(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "NO MATCH")
        assert len(list(result.get_nodes())) == 0
        assert len(list(result.get_edges())) == 0

    def test_match_by_key_name(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "city")
        assert len(list(result.get_nodes())) == 3

    def test_edges_preserved_for_matched_nodes(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "Berlin")
        assert len(list(result.get_edges())) == 1

    def test_edge_dropped_if_one_endpoint_missing(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "Alice")
        assert len(list(result.get_edges())) == 0

    def test_original_graph_not_modified(self):
        graph = make_graph()
        before_nodes = len(list(graph.get_nodes()))
        QueryEngine.search(graph, "Alice")
        assert len(list(graph.get_nodes())) == before_nodes

    def test_result_nodes_are_copies(self):
        graph = make_graph()
        result = QueryEngine.search(graph, "Alice")
        result_node = next(iter(result.get_nodes()))
        original = next(node for node in graph.get_nodes() if node.attributes.get("name") == "Alice")
        assert result_node is not original

# ───────────────── filter ─────────────────

class TestFilter:
    def test_filter_equal_int(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age == 30")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice"}

    def test_filter_greater_than(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age > 25")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice", "Carol"}

    def test_filter_greater_or_equal(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age >= 30")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice", "Carol"}

    def test_filter_less_than(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age < 30")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Bob"}

    def test_filter_less_or_equal(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age <= 30")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice", "Bob"}

    def test_filter_not_equal(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "city != 'Berlin'")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Carol"}

    def test_filter_string_equal(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "city == Berlin")
        names = {node.attributes["name"] for node in result.get_nodes()}
        assert names == {"Alice", "Bob"}

    def test_filter_missing_attribute_skipped(self):
        graph = Graph(directed=True)
        first_node = Node()
        first_node.set_attributes({"age": 20})
        second_node = Node()
        second_node.set_attributes({"score": 99})
        graph.add_node(first_node)
        graph.add_node(second_node)
        result = QueryEngine.filter(graph, "age > 10")
        assert len(list(result.get_nodes())) == 1

    def test_filter_type_mismatch_raises(self):
        graph = Graph(directed=True)
        node = Node()
        node.set_attributes({"age": "thirty"})
        graph.add_node(node)
        with pytest.raises(Exception, match="Types do not match"):
            QueryEngine.filter(graph, "age > 10")

    def test_filter_no_match_empty_graph(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age > 100")
        assert len(list(result.get_nodes())) == 0

    def test_filter_preserves_edges(self):
        graph = make_graph()
        result = QueryEngine.filter(graph, "age < 35")
        assert len(list(result.get_edges())) == 1

    def test_filter_with_date(self):
        graph = Graph(directed=True)
        first_node, second_node = Node(), Node()
        first_node.set_attributes({"born": datetime.date(1990, 1, 1)})
        second_node.set_attributes({"born": datetime.date(2000, 6, 15)})
        graph.add_node(first_node)
        graph.add_node(second_node)
        result = QueryEngine.filter(graph, "born > 01.01.1995.")
        nodes = list(result.get_nodes())
        assert len(nodes) == 1
        assert nodes[0].attributes["born"] == datetime.date(2000, 6, 15)

    def test_filter_unsupported_operator_raises(self):
        node = Node()
        node.set_attributes({"age": 10})
        expression = FilterExpression("age", "??", 5)
        with pytest.raises(Exception, match="not supported"):
            QueryEngine.is_valid_node(node, expression)


# ───────────────── subgraph building ─────────────────

class TestBuildSubgraph:
    def test_empty_node_list(self):
        graph = make_graph()
        result = QueryEngine.build_subgraph([], graph)
        assert len(list(result.get_nodes())) == 0
        assert len(list(result.get_edges())) == 0

    def test_directionality_preserved(self):
        graph_directed = Graph(directed=True)
        graph_undirected = Graph(directed=False)
        node = Node()
        graph_directed.add_node(node)
        graph_undirected.add_node(node)
        assert QueryEngine.build_subgraph([node.copy(keep_id=True)], graph_directed).is_directed() is True
        assert QueryEngine.build_subgraph([node.copy(keep_id=True)], graph_undirected).is_directed() is False

    def test_nodes_are_fresh_copies(self):
        graph = make_graph()
        original_nodes = list(graph.get_nodes())
        result = QueryEngine.build_subgraph([node.copy(keep_id=True) for node in original_nodes], graph)
        result_ids = {node.id for node in result.get_nodes()}
        original_ids = {node.id for node in original_nodes}
        assert result_ids == original_ids
        for result_node in result.get_nodes():
            original = next(node for node in original_nodes if node.id == result_node.id)
            assert result_node is not original