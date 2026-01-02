import uuid
from typing import List, Dict

from api.src.api.model import Graph
from api.src.api.model.graph import Node


class QueryEngine:

    @staticmethod
    def search(graph: Graph, text: str) -> Graph:
        valid_nodes: List[Node] = []
        for node in graph.get_nodes():
            for key, value in node.attributes.items():
                if text.lower() in str(key).lower() or text.lower() in str(value).lower():
                    valid_nodes.append(node.copy(True))
                    break
        new_graph: Graph = QueryEngine.build_subgraph(valid_nodes, graph)
        return new_graph

    @staticmethod
    def filter(graph: Graph, expression: str) -> Graph:
        pass

    @staticmethod
    def build_subgraph(nodes: List[Node], graph: Graph) -> Graph:
        new_graph: Graph = Graph(graph.is_directed())
        map_nodes : Dict[uuid.UUID, Node] = {}
        for node in nodes:
            node_copy : Node = node.copy()
            map_nodes[node.id] = node_copy
            new_graph.add_node(node_copy)
        for edge in graph.get_edges():
            if edge.source.id in map_nodes and edge.target.id in map_nodes:
                new_graph.add_edge(edge.copy(map_nodes[edge.source.id], map_nodes[edge.target.id]))
        return new_graph