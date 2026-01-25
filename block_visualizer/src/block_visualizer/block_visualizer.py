from api.model import Graph
from api.plugins import VisualizerPlugin

class BlockVisualizer(VisualizerPlugin):
    def name(self) -> str:
        return "Block Visualizer"

    def identifier(self) -> str:
        return "block_visualizer"

    def render(self, graph:Graph, **kwargs) -> str:
        graph_str = ""
        for node in graph.get_nodes():
            graph_str += f"id: {node.id}\n"
            for key in node.attributes:
                graph_str += f"\t{key}: {node.attributes[key]}\n"
        for edge in graph.get_edges():
            graph_str += f"\t{edge.id}\n"
            graph_str += f"\t{edge.source.id} - {edge.target.id}\n"
            for key in edge.attributes:
                graph_str += f"\t{key}: {edge.attributes[key]}\n"
        return graph_str
