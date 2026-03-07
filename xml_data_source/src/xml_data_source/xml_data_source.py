import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from datetime import datetime

from api.model import *
from api.plugins import DataSourcePlugin


class XmlDataSource(DataSourcePlugin):
    """A DataSourcePlugin that builds a Graph by parsing an XML file.

    Each XML element with children becomes a Node. Leaf elements (no children)
    are treated as attributes of their parent node. Relationships between nodes
    are created both from the XML hierarchy (parent-child edges) and from
    reference attributes that point to other nodes by their id.
    """

    def name(self) -> str:
        """Return the human-readable name of this data source."""
        return "XML Data Source"

    def identifier(self) -> str:
        """Return the unique machine-readable identifier of this data source."""
        return "xml_data_source"

    def fields(self) -> Dict[str, str]:
        """Return the configuration fields required by this data source.

        The returned dict maps field names to their UI input types:
          directed               -- checkbox; whether the resulting graph is directed
          file_path              -- file; path to the XML file to load
          reference_source_attr  -- text; attribute name used as the node identifier (default: 'id')
          reference_target_attrs -- text; comma-separated attribute names that reference other nodes
        """
        return {
            "directed": "checkbox",
            "file_path": "file",
            "reference_source_attr": "text",
            "reference_target_attrs": "text"
        }

    def load(self, **kwargs) -> Graph:
        """Load an XML file and return its contents as a Graph.

        Raises AttributeError if 'file_path' is not provided.

        Keyword arguments:
        file_path              -- (required) path to the XML file to parse
        directed               -- (optional) whether the graph is directed; defaults to False
        reference_source_attr  -- (optional) attribute used as node id; defaults to 'id'
        reference_target_attrs -- (optional) comma-separated list of attributes that
                                  reference other nodes by id; defaults to
                                  'reportsTo,assignedProject,assignedTo'
        """

        file_path: str = kwargs.get("file_path")
        if file_path is None:
            raise AttributeError("file_path is required")

        directed: bool = kwargs.get("directed", False)

        reference_source_attr: str = kwargs.get("reference_source_attr") or "id"
        reference_target_attrs_raw: str = kwargs.get("reference_target_attrs") or "reportsTo,assignedProject,assignedTo"
        reference_target_attrs: List[str] = [x.strip() for x in reference_target_attrs_raw.split(",")]

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
    ) -> Optional[Node]:
        """Recursively parse an XML element into nodes and edges in the graph.

        Elements with children become Nodes. Leaf elements (no children) are
        stored as attributes on their parent node instead. XML attributes on
        non-leaf elements are added as node attributes. An Edge is created
        between a parent node and each child node, with the 'relation' attribute
        set to the child's tag name.

        Returns the Node created for a non-leaf element, or None for leaf elements.

        Keyword arguments:
        element     -- the XML element to parse
        graph       -- the Graph being populated
        id_to_node  -- mapping of id attribute values to their Nodes,
                       used later by resolve_references
        parent_node -- the Node that owns the current element (default None)
        relation    -- the tag name under which this element appears in the parent (default None)
        """

        if len(element) == 0:
            if parent_node is not None and element.text and element.text.strip():
                parsed_value = self.parse_attribute_value(element.text.strip())
                parent_node.add_attribute(element.tag, parsed_value)
            return None

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
        """Create edges for reference attributes that point to other nodes by id.

        Walks all elements in the tree. For each element that has the source
        attribute (e.g. 'id'), checks whether any of the target attributes
        (e.g. 'reportsTo') contain the id of another known node. If both the
        source and target nodes exist in id_to_node, an Edge is added between
        them with the 'relation' attribute set to the target attribute name.
        This is also how cyclic references are resolved.

        Keyword arguments:
        root         -- the root XML element to iterate over
        graph        -- the Graph to add edges to
        id_to_node   -- mapping of id values to Nodes built during parse_element
        source_attr  -- the attribute name used to identify the current node (e.g. 'id')
        target_attrs -- list of attribute names that may reference another node by id
        """
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
        """Coerce a raw string value to the most specific matching type.

        Types are attempted in this order:
          1. int
          2. float
          3. date (format: YYYY-MM-DD)
          4. date (format: DD.MM.YYYY.)
          5. bool ('true' / 'false', case-insensitive)
          6. str  (returned as-is if nothing else matches)

        Keyword arguments:
        value -- the raw string value to coerce
        """

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