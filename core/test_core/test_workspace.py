from typing import Dict

from api.model import Graph, Node, Edge
from api.plugins import DataSourcePlugin, VisualizerPlugin
from use_cases import Workspace

class DataSourcePluginMock(DataSourcePlugin):
    def name(self) -> str:
        return 'DSP Mock'

    def identifier(self) -> str:
        return 'dsp_mock'

    def fields(self) -> Dict[str, str]:
        return {}

    def load(self, **kwargs) -> Graph:
        graph = Graph(True)
        nodes = [Node(), Node(), Node()]
        edges = [Edge(nodes[0], nodes[1]), Edge(nodes[1], nodes[2])]
        for node in nodes:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)
        return graph

class VisualizerPluginMock(VisualizerPlugin):
    def name(self) -> str:
        return 'VP Mock'

    def identifier(self) -> str:
        return 'vp_mock'

    def serialize_edge(edge: Edge) -> str:
        return f"{str(edge.source.id)}-{str(edge.target.id)}"

    def serialize_node(node: Node) -> str:
        return str(node.id)

    def render(self, graph: Graph, **kwargs) -> str:
        graph_vis = ""
        for node in graph.get_nodes():
            graph_vis += f"{VisualizerPluginMock.serialize_node(node)}/n"
        for edge in graph.get_edges():
            graph_vis += f"{VisualizerPluginMock.serialize_edge(edge)}/n"
        return graph_vis

def load_workspace():
    workspace = Workspace()
    workspace.set_data_source(DataSourcePluginMock())
    workspace.set_visualizer(VisualizerPluginMock())
    return workspace

class TestWorkspaceInit:

    def test_initial_state(self):
        ws = Workspace()
        assert ws.base_graph is None
        assert ws.graph is None
        assert ws.data_source is None
        assert ws.visualizer is None
        assert ws.queries == []

class TestSetPlugins:

    def test_set_data_source(self):
        ws = Workspace()
        dsp = DataSourcePluginMock()
        ws.set_data_source(dsp)
        assert ws.data_source is dsp

    def test_set_visualizer(self):
        ws = Workspace()
        vp = VisualizerPluginMock()
        ws.set_visualizer(vp)
        assert ws.visualizer is vp

class TestLoadAndRender:

    def test_sets_base_graph(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        assert workspace.base_graph is not None

    def test_graph_equals_base_graph_after_load(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        assert workspace.graph is workspace.base_graph

    def test_clears_queries_on_load(self):
        workspace = load_workspace()
        workspace.queries = [{"type": "search", "text": "name"}]
        workspace.load_and_render({})
        assert workspace.queries == []

    def test_returns_render_output(self):
        workspace = load_workspace()
        result = workspace.load_and_render({})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_reload_resets_previous_graph_state(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        first_graph = workspace.base_graph
        workspace.load_and_render({})
        assert workspace.base_graph is not first_graph

class TestApplyQueries:

    def test_queries_create_filtered_graph(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        queries = [{"type": "search", "text": "name"}]
        workspace.apply_queries(queries)
        assert workspace.queries == queries
        assert workspace.graph is not workspace.base_graph

    def test_returns_render_output(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        queries = [{"type": "search", "text": "name"}]
        workspace.apply_queries(queries)
        result = workspace.load_and_render({})
        assert isinstance(result, str)

    def test_empty_query_list_keeps_base_graph(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        workspace.apply_queries([])
        assert workspace.graph is workspace.base_graph

    def test_does_not_mutate_base_graph(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        base = workspace.base_graph
        query = {"type": "filter", "attribute": "x", "operator": "=", "value": "1"}
        workspace.apply_queries([query])
        assert workspace.base_graph is base

class TestClearQueries:

    def test_clears_query_list(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        workspace.queries = [{"type": "search", "text": "foo"}]
        workspace.clear_queries()
        assert not workspace.queries

    def test_resets_graph_to_base(self):
        workspace = load_workspace()
        workspace.load_and_render({})
        workspace.apply_queries([])
        workspace.clear_queries()
        assert workspace.graph is workspace.base_graph