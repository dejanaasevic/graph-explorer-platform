from api.model import Graph
from api.plugins import DataSourcePlugin, VisualizerPlugin
from typing import Dict, List
from .cli_proxy import CLIProxy
from use_cases.query_engine import QueryEngine


class Workspace(object):
    """
    Object representing a workspace.

    It encapsulates data about the graph, applied plugins and graph queries.
    """
    def __init__(self):
        self.base_graph: Graph = None
        self.graph: Graph = None
        self.data_source: DataSourcePlugin = None
        self.visualizer: VisualizerPlugin = None
        self.cli: CLIProxy = None
        self.queries: List[Dict[str, str]] = []

    def set_data_source(self, data_source: DataSourcePlugin):
        """
        Sets the data source for the workspace.
        """
        self.data_source = data_source

    def set_visualizer(self, visualizer: VisualizerPlugin):
        """
        Sets the visualizer for the workspace.
        """
        self.visualizer = visualizer
        self.cli = CLIProxy(self.visualizer)

    def load_and_render(self, kwargs: Dict[str, str]):
        """
        Encapsulates the application data flow.

        Data Source plugins transform the external data into a Graph object,
        which is then rendered by the visualizer plugin and returned in a string representation.
        """
        self.base_graph = self.data_source.load(**kwargs)
        self.graph = self.base_graph
        self.queries = []
        return self.visualizer.render(self.base_graph)

    def apply_queries(self, queries: List[Dict[str, str]]):
        self.queries = queries
        current: Graph = self.base_graph
        for query in queries:
            if query["type"] == "search":
                current = QueryEngine.search(current, query["text"])
            elif query["type"] == "filter":
                expression = f"{query['attribute']} {query['operator']} {query['value']}"
                current = QueryEngine.filter(current, expression)
        self.graph = current
        return self.visualizer.render(current)

    def clear_queries(self):
        self.queries = []
        self.graph = self.base_graph
        return self.visualizer.render(self.base_graph)