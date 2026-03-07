from use_cases import CLI
from use_cases.cli import InvalidArgumentException
import datetime
import uuid
import pytest

from api.model import Graph, Node, Edge

def make_empty_graph():
    graph = Graph(True)
    return graph

class TestParseAttributes:

    def test_int_attribute(self):
        result = CLI.parse_attributes(["--int", "age=30"], False)
        assert result == {"age": 30}

    def test_float_attribute(self):
        result = CLI.parse_attributes(["--float", "score=9.5"], False)
        assert result == {"score": 9.5}

    def test_string_attribute_simple(self):
        result = CLI.parse_attributes(["--string", "name=Alice"], False)
        assert result == {"name": "Alice"}

    def test_string_attribute_quoted_multiword(self):
        args = ["--string", "name='hello", "world'"]
        result = CLI.parse_attributes(args, False)
        assert result == {"name": "hello world"}

    def test_string_attribute_unclosed_quote_raises(self):
        args = ["--string", "name='unclosed"]
        with pytest.raises(InvalidArgumentException, match="Improperly formatted string input"):
            CLI.parse_attributes(args, False)

    def test_date_attribute_valid(self):
        result = CLI.parse_attributes(["--date", "dob=15.06.1990"], False)
        assert result == {"dob": datetime.date(1990, 6, 15)}

    def test_date_attribute_invalid_format_raises(self):
        with pytest.raises(InvalidArgumentException, match="DD.MM.YYYY"):
            CLI.parse_attributes(["--date", "dob=1990-06-15"], False)

    def test_delete_attribute_in_update_mode(self):
        result = CLI.parse_attributes(["--delete", "age"], True)
        assert result == {"age": None}

    def test_delete_attribute_in_create_mode_raises(self):
        with pytest.raises(InvalidArgumentException, match="can't use the --delete"):
            CLI.parse_attributes(["--delete", "age"], False)

    def test_unknown_flag_raises(self):
        with pytest.raises(InvalidArgumentException, match="Invalid argument"):
            CLI.parse_attributes(["--unknown", "x=1"], False)

    def test_multiple_attributes(self):
        args = ["--int", "age=25", "--string", "name=Bob", "--float", "score=7.8"]
        result = CLI.parse_attributes(args, False)
        assert result == {"age": 25, "name": "Bob", "score": 7.8}

    def test_empty_args_returns_empty_dict(self):
        assert CLI.parse_attributes([], False) == {}

class TestCreateNode:

    def test_create_node_no_attributes(self):
        graph = make_empty_graph()
        result = CLI.create_node(graph, [])
        assert result in graph.get_nodes()

    def test_create_node_with_attributes(self):
        graph = make_empty_graph()
        result = CLI.create_node(graph, ["--int", "age=42"])
        assert result in graph.get_nodes()
        assert result.attributes["age"] == 42

class TestCreateEdge:

    def test_create_edge_success(self):
        graph = make_empty_graph()
        source = Node()
        target = Node()
        graph.add_node(source)
        graph.add_node(target)

        result = CLI.create_edge(graph, [str(source.id), str(target.id)])

        assert result in graph.get_edges()
        assert result.source is source
        assert result.target is target

    def test_create_edge_missing_target_raises(self):
        graph = make_empty_graph()
        source = Node()
        graph.add_node(source)

        with pytest.raises(InvalidArgumentException, match="does not exist"):
            result = CLI.create_edge(graph, [str(source.id), str(uuid.uuid4())])

    def test_create_edge_missing_source_raises(self):
        graph = make_empty_graph()
        target = Node()
        graph.add_node(target)

        with pytest.raises(InvalidArgumentException, match="does not exist"):
            result = CLI.create_edge(graph, [str(uuid.uuid4()), str(target.id)])

    def test_create_edge_with_attributes(self):
        graph = make_empty_graph()
        source = Node()
        target = Node()
        graph.add_node(source)
        graph.add_node(target)

        result = CLI.create_edge(graph, [str(source.id), str(target.id), "--string", "label=connects"])

        assert result in graph.get_edges()
        assert result.source is source
        assert result.target is target
        assert result.attributes["label"] == "connects"

class TestDeleteNode:

    def test_delete_node_success(self):
        graph = make_empty_graph()
        node = Node()
        graph.add_node(node)
        CLI.delete_node(graph, str(node.id))
        assert node not in graph.get_nodes()

    def test_delete_node_not_found_raises(self):
        graph = make_empty_graph()
        with pytest.raises(InvalidArgumentException, match="does not exist"):
            CLI.delete_node(graph, str(uuid.uuid4()))

class TestDeleteEdge:

    def test_delete_edge_success(self):
        graph = make_empty_graph()
        source = Node()
        target = Node()
        graph.add_node(source)
        graph.add_node(target)
        edge = Edge(source, target)
        graph.add_edge(edge)

        CLI.delete_edge(graph, str(source.id), str(target.id))

        assert edge not in graph.get_edges()

    def test_delete_edge_not_found_raises(self):
        graph = make_empty_graph()
        with pytest.raises(InvalidArgumentException, match="does not exist"):
            CLI.delete_edge(graph, str(uuid.uuid4()), str(uuid.uuid4()))

class TestUpdateNode:

    def test_update_node_set_attribute(self):
        graph = make_empty_graph()
        node = Node()
        node.set_attributes({"age": 20})
        graph.add_node(node)

        result = CLI.update_node(graph, [str(node.id), "--int", "age=30"])

        assert node.attributes["age"] == 30
        assert result is node

    def test_update_node_delete_attribute(self):
        graph = make_empty_graph()
        node = Node()
        node.set_attributes({"age": 20})
        graph.add_node(node)

        CLI.update_node(graph, [str(node.id), "--delete", "age"])

        assert "age" not in node.attributes

    def test_update_node_delete_nonexistent_attribute_is_noop(self):
        graph = make_empty_graph()
        node = Node()
        node.set_attributes({"age": 20})
        graph.add_node(node)

        CLI.update_node(graph, [str(node.id), "--delete", "missing"])

        assert "missing" not in node.attributes

    def test_update_node_not_found_raises(self):
        graph = make_empty_graph()
        with pytest.raises(InvalidArgumentException, match="does not exist"):
            CLI.update_node(graph, [str(uuid.uuid4()), "--int", "x=1"])


# ===========================================================================
# update_edge
# ===========================================================================

class TestUpdateEdge:

    def test_update_edge_set_attribute(self):
        graph = make_empty_graph()
        source = Node()
        target = Node()
        graph.add_node(source)
        graph.add_node(target)
        edge = Edge(source, target)
        graph.add_edge(edge)

        result = CLI.update_edge(graph, [str(edge.id), "--float", "weight=2.5"])

        assert edge.attributes["weight"] == 2.5
        assert result is edge

    def test_update_edge_delete_attribute(self):
        graph = make_empty_graph()
        source = Node()
        target = Node()
        graph.add_node(source)
        graph.add_node(target)
        edge = Edge(source, target)
        edge.set_attributes({"weight": 2.5})
        graph.add_edge(edge)

        CLI.update_edge(graph, [str(edge.id), "--delete", "weight"])

        assert "weight" not in edge.attributes

    def test_update_edge_not_found_raises(self):
        graph = make_empty_graph()
        with pytest.raises(InvalidArgumentException, match="does not exist"):
            CLI.update_edge(graph, [str(uuid.uuid4())])

class TestClear:

    def test_clear_removes_all_edges_then_nodes(self):
        graph = make_empty_graph()
        source = Node()
        target = Node()
        graph.add_node(source)
        graph.add_node(target)
        edge = Edge(source, target)
        graph.add_edge(edge)

        CLI.clear(graph)

        assert not graph.get_nodes()
        assert not graph.get_edges()