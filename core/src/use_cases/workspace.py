from api.model import Graph
from api.plugins import DataSourcePlugin, VisualizerPlugin
from typing import Dict

from .cli_proxy import CLIProxy


class Workspace(object):
    """
    Object representing a workspace.

    It encapsulates data about the graph, applied plugins and graph queries.
    """
    def __init__(self):
        self.graph: Graph = None
        self.data_source: DataSourcePlugin = None
        self.visualizer: VisualizerPlugin = None
        self.cli: CLIProxy = None

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
        self.graph = self.data_source.load(**kwargs)
        return self.visualizer.render(self.graph)