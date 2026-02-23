import uuid
from typing import List, Dict

from api.model import Graph
from api.model import Node
from use_cases.query_parser import FilterExpression, Parser


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
        filter_expression: FilterExpression = Parser.parse(expression)
        valid_nodes: List[Node] = []
        for node in graph.get_nodes():
            if node.attributes.get(filter_expression.attribute.lower()) is None:
                continue
            if QueryEngine.is_valid_node(node, filter_expression):
                valid_nodes.append(node.copy(True))
        new_graph: Graph = QueryEngine.build_subgraph(valid_nodes, graph)
        return new_graph

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

    @staticmethod
    def is_valid_node(node: Node, filter_expression: FilterExpression) -> bool:
        attribute_value = node.attributes.get(filter_expression.attribute.lower())

        if attribute_value is None:
            return False

        if not (isinstance(attribute_value, type(filter_expression.value)) or
                (isinstance(attribute_value, (int, float)) and isinstance(filter_expression.value, (int, float)))):
            raise Exception(
                f"error: Types do not match! Attribute: {type(attribute_value)}, filter value: {type(filter_expression.value)}")

        match filter_expression.operator:
            case "==":
                return attribute_value == filter_expression.value
            case ">":
                return attribute_value > filter_expression.value
            case ">=":
                return attribute_value >= filter_expression.value
            case "<":
                return attribute_value < filter_expression.value
            case "<=":
                return attribute_value <= filter_expression.value
            case "!=":
                return attribute_value != filter_expression.value
            case _: raise Exception(f"error: operator {filter_expression.operator} is not supported!")