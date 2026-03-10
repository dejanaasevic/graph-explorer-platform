import datetime
import json
from typing import Dict, Any

from api.model import *
from api.plugins import DataSourcePlugin


class JsonDataSource(DataSourcePlugin):
    """A DataSourcePlugin that builds a Graph by loading a JSON file.

    Nested dicts become nodes, and nested relationships become edges
    with a 'relation' attribute. Nodes can reference each other by
    an optional '@id' field, which is resolved into edges.
    """

    def name(self) -> str:
        """Return the human-readable name of this data source."""
        return "Json Data Source"

    def identifier(self) -> str:
        """Return the unique machine-readable identifier of this data source."""
        return "json_data_source"

    def fields(self) -> Dict[str, str]:
        """Return the configuration fields required by this data source.

        The returned dict maps field names to their UI input types:
          directed  -- checkbox; whether the resulting graph should be directed
          file_path -- file; the path to the JSON file to load
        """
        return {"directed": "checkbox", "file_path": "file"}

    def load(self, **kwargs) -> Graph:
        """Load a JSON file and return its contents as a Graph.

        Raises AttributeError if 'file_path' is not provided.

        Keyword arguments:
        file_path -- (required) path to the JSON file to parse
        directed  -- (optional) whether the graph is directed; defaults to False
        """
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
        """Recursively parse a JSON structure into nodes and edges in the graph.

        Each JSON dict becomes a Node. Nested dicts and list items that are
        dicts become child nodes connected to their parent by an Edge whose
        'relation' attribute is set to the parent key. String values that
        match a previously seen '@id' are resolved as edges rather than
        plain attributes. Scalar values (int, float, str) are coerced via
        parse_attribute_value before being stored as node attributes.

        Returns the Node created for a dict, or None for non-dict input.

        Keyword arguments:
        data        -- the JSON value to parse (dict, list, scalar, or None)
        graph       -- the Graph being populated
        id_to_node  -- mapping of '@id' strings to their corresponding Nodes,
                       used to resolve cross-references
        parent_node -- the Node that owns the current value (default None)
        relation    -- the key under which this value appears in the parent dict (default None)
        """
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
                        edge: Edge = Edge(node, id_to_node.get(value))
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
        """Coerce a raw scalar value to the most specific matching type.

        Types are attempted in this order:
          1. int
          2. float
          3. date  (expected format: DD.MM.YYYY.)
          4. str   (surrounding single or double quotes are stripped)

        Keyword arguments:
        value -- the raw value to coerce; typically a str, int, or float
        """
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