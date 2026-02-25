import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from datetime import datetime

from api.model import *
from api.plugins import DataSourcePlugin


class XmlDataSource(DataSourcePlugin):

    def name(self) -> str:
        return "XML Data Source"

    def identifier(self) -> str:
        return "xml_data_source"

    def load(self, **kwargs) -> Graph:
        file_path: str = kwargs.get("file_path")
        if file_path is None:
            raise AttributeError("file_path is required")

        directed: bool = kwargs.get("directed", True)

        reference_source_attr: str = kwargs.get("reference_source_attr", "id")
        reference_target_attrs: List[str] = kwargs.get(
            "reference_target_attrs",
            ["reportsTo", "assignedProject", "assignedTo"]
        )

        graph = Graph(directed=directed)
        id_to_node: Dict[str, Node] = {}

        tree = ET.parse(file_path)
        root = tree.getroot()

        self.parse_element(root, graph, id_to_node)

        self.resolve_references(
            root,
            graph,
            id_to_node,
            reference_source_attr,
            reference_target_attrs
        )

        return graph

    def parse_element(
            self,
            element: ET.Element,
            graph: Graph,
            id_to_node: Dict[str, Node],
            parent_node: Optional[Node] = None,
            relation: Optional[str] = None,
    ) -> Node:

        node = Node()

        node.add_attribute("tag", element.tag)

        element_id = element.attrib.get("id")
        if element_id:
            id_to_node[element_id] = node

        for key, value in element.attrib.items():
            parsed_value = self.parse_attribute_value(value)
            node.add_attribute(key, parsed_value)

        graph.add_node(node)

        if parent_node is not None:
            edge = Edge(parent_node, node)
            edge.add_attribute("relation", relation or element.tag)
            graph.add_edge(edge)

        if element.text and element.text.strip():
            node.add_attribute(
                "text",
                self.parse_attribute_value(element.text.strip())
            )

        for child in element:
            self.parse_element(child, graph, id_to_node, node, child.tag)

        return node

    def resolve_references(
            self,
            root: ET.Element,
            graph: Graph,
            id_to_node: Dict[str, Node],
            source_attr: str,
            target_attrs: List[str],
    ):

        for element in root.iter():

            source_id = element.attrib.get(source_attr)
            if not source_id:
                continue

            for target_attr in target_attrs:
                target_id = element.attrib.get(target_attr)

                if target_id:
                    if source_id in id_to_node and target_id in id_to_node:
                        edge = Edge(
                            id_to_node[source_id],
                            id_to_node[target_id]
                        )
                        edge.add_attribute("relation", target_attr)
                        graph.add_edge(edge)

    @staticmethod
    def parse_attribute_value(value: str) -> Any:

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass

        try:
            return datetime.strptime(value, "%d.%m.%Y.").date()
        except ValueError:
            pass

        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        return value