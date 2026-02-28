from api.model import Graph
from api.plugins import DataSourcePlugin, VisualizerPlugin
from .cli import CLI
from typing import Dict

class Workspace(object):
    def __init__(self):
        self.graph: Graph = None
        self.data_source: DataSourcePlugin = None
        self.visualizer: VisualizerPlugin = None
        self.cli: CLI = None

    def set_data_source(self, data_source: DataSourcePlugin):
        self.data_source = data_source

    def set_visualizer(self, visualizer: VisualizerPlugin):
        self.visualizer = visualizer

    def load_and_render(self, kwargs: Dict[str, str]):
        self.graph = self.data_source.load(**kwargs)
        self.cli = CLI(self.graph)
        return self.visualizer.render(self.graph)