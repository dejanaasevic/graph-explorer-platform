import datetime
import json
from typing import Dict, Any

from api.model import *
from api.plugins import DataSourcePlugin

class JsonDataSource(DataSourcePlugin):
    def name(self) -> str:
        return "Json Data Source"

    def identifier(self) -> str:
        return "json_data_source"

    def fields(self) -> Dict[str,str]:
        return {"directed": "checkbox", "file_path": "text"}

    def load(self, **kwargs) -> Graph:
        file_path: str = kwargs.get("file_path")
        if file_path is None:
            raise AttributeError("file_path is required")

        directed: bool = kwargs.get("directed", False)

        graph: Graph = Graph(directed=directed)
        id_to_node: Dict[str, Node] = {}

        with open(file_path) as file:
            data = json.load(file)

        self.parse_json(data, graph, id_to_node)

        return graph

    def parse_json(self, data: Any, graph: Graph, id_to_node: Dict[str, Node],
                   parent_node: Node = None, relation: str = None):
        if isinstance(data, dict):
            node: Node = Node()

            if data.get("@id") is not None:
                id_to_node[data.get("@id")] = node

            graph.add_node(node)

            for key, value in data.items():
                if key == "@id":
                    continue

                if value is None:
                    node.add_attribute(key, None)
                    continue

                if isinstance(value, dict):
                    child_node = self.parse_json(value, graph, id_to_node, node, key)
                    if child_node is not None:
                        edge: Edge = Edge(node, child_node)
                        edge.add_attribute("relation", key)
                        graph.add_edge(edge)

                elif isinstance(value, (int, float)):
                    value = self.parse_attribute_value(value)
                    node.add_attribute(key, value)

                elif isinstance(value, str):
                    if id_to_node.get(value) is not None:
                        edge : Edge = Edge(node, id_to_node.get(value))
                        edge.add_attribute("relation", key)
                        graph.add_edge(edge)
                    else:
                        value = self.parse_attribute_value(value)
                        node.add_attribute(key, value)

                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            child_node = self.parse_json(item, graph, id_to_node, node, key)
                            if child_node is not None:
                                edge: Edge = Edge(node, child_node)
                                edge.add_attribute("relation", key)
                                graph.add_edge(edge)
            return node
        return None

    @staticmethod
    def parse_attribute_value(value: Any) -> Any:
        try:
            value_parsed: Any = int(value)
        except ValueError:
            try:
                value_parsed = float(value)
            except ValueError:
                try:
                    value_parsed = datetime.datetime.strptime(value, "%d.%m.%Y.").date()
                except ValueError:
                    value_parsed = value.strip('"').strip("'")
        return value_parsed
