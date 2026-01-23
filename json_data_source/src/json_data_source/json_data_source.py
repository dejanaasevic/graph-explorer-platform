import json
from typing import Dict, Any

from api.model import *
from api.plugins import DataSourcePlugin

class JsonDataSource(DataSourcePlugin):
    def name(self) -> str:
        return "Json Data Source"

    def identifier(self) -> str:
        return "json_data_source"

    def load(self, **kwargs) -> Graph:
        file_path : str = kwargs.get("file_path")
        if file_path is None:
            raise AttributeError("file_path is required")

        directed : bool = kwargs.get("directed", True)

        graph : Graph = Graph(directed=directed)
        id_to_node : Dict[str, Node] = {}

        with open(file_path) as file:
            data = json.load(file)

        self.parse_json(data, graph, id_to_node)

        return graph

    def parse_json(self, data : Any, graph : Graph, id_to_node : Dict[str, Node],
                   parent_node : Node = None, relation : str = None):
        pass