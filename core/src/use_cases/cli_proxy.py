from .cli import CLI
from api.plugins import VisualizerPlugin
from api.model import Graph, Node, Edge

class CLIProxy(object):
    def __init__(self, visualizer: VisualizerPlugin):
        self.visualizer = visualizer

    def parse_command(self, graph, command):
        result = CLI.parse_command(graph, command)
        if isinstance(result, Node):
            return self.visualizer.serialize_node(result)
        if isinstance(result, Edge):
            return self.visualizer.serialize_edge(result)