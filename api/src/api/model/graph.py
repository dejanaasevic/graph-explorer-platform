import uuid
from typing import Dict, Any


class Node:
    def __init__(self, attributes: Dict[str, Any] = None ):
        self.node_id : uuid.UUID = uuid.uuid4()
        self.attributes : Dict[str, Any] = attributes or {}

    def __repr__(self):
        return f"Node(id={self.node_id}, attributes={self.attributes})"

class Edge:
    def __init__(self, source : Node, target : Node, attributes: Dict[str, Any] = None):
        self.id : uuid.UUID = uuid.uuid4()
        self.source : Node = source
        self.target : Node = target
        self.attributes: Dict[str, Any] = attributes or {}

    def __repr__(self):
        return f"Edge({self.source.node_id} --> {self.target.node_id})"
