import uuid
from typing import Dict, Any


class Node:
    def __init__(self, attributes: Dict[str, Any] = None ):
        self.node_id : uuid.UUID = uuid.uuid4()
        self.attributes : Dict[str, Any] = attributes or {}

    def __repr__(self):
        return f"Node(id={self.node_id}, attributes={self.attributes})"
