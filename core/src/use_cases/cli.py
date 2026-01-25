from datetime import datetime
from typing import Any
from uuid import UUID

from api.model import Graph, Node, Edge

class InvalidArgumentException(Exception):
    pass

class CLI(object):
    def __init__(self, graph: Graph):
        self.graph = graph

    def parse_command(self, command: str):
        parsed = command.split(' ')
        try:
            match parsed[0]:
                case 'create-node':
                    self.create_node(parsed[1:])
                    print("Created new node!")
                case 'create-edge':
                    self.create_edge(parsed[1:])
                    print("Created new edge!")
                case 'update-node':
                    self.update_node(parsed[1:])
                    print("Updated node!")
                case 'update-edge':
                    self.update_edge(parsed[1:])
                    print("Updated edge!")
                case 'delete-node':
                    self.delete_node(parsed[1])
                    print("Removed node!")
                case 'delete-edge':
                    self.delete_edge(parsed[1])
                    print("Removed edge!")
                case 'clear':
                    self.clear()
                    print("Graph cleared!")
                case _:
                    print(f'Unknown command: {parsed[0]}')
        except Exception as e:
            print(e)

    def parse_attributes(self, args: list[str], update: bool) -> dict[str, Any]:
        option = None
        attributes: dict[str, Any] = {}
        i = 0
        while i < len(args):
            if args[i][0] == '-':
                option = args[i][2:]
            else:
                match option:
                    case 'int':
                        name, raw_value = args[i].split('=')
                        attributes[name] = int(raw_value)
                    case 'float':
                        name, raw_value = args[i].split('=')
                        attributes[name] = float(raw_value)
                    case 'string':
                        name, raw_value = args[i].split('=')
                        if raw_value[0] == "'":
                            try:
                                while args[i][-1] != "'":
                                    i += 1
                                    raw_value += ' '
                                    raw_value += args[i]
                            except IndexError:
                                raise InvalidArgumentException("Improperly formatted string input!")
                            attributes[name] = raw_value[1:-1]
                        else:
                            attributes[name] = raw_value
                    case 'date':
                        name, raw_value = args[i].split('=')
                        try:
                            attributes[name] = datetime.strptime(raw_value, "%d.%m.%Y").date()
                        except ValueError:
                            raise InvalidArgumentException("Dates must be in DD.MM.YYYY format")
                    case 'delete':
                        name = args[i]
                        if not update:
                            raise InvalidArgumentException("create-* commands can't use the --delete argument!")
                        attributes[name] = None
                    case _:
                        raise InvalidArgumentException(f"Invalid argument --{option}!")
            i += 1
        return attributes

    def create_node(self, args: list[str]):
        attributes: dict[str, Any] = self.parse_attributes(args, False)
        new_node = Node(attributes)
        self.graph.add_node(new_node)

    def create_edge(self, args: list[str]):
        source: Node = self.graph.get_node(UUID(args[0]))
        target: Node = self.graph.get_node(UUID(args[1]))
        if source is None:
            raise InvalidArgumentException(f"Node with ID {args[0]} does not exist!")
        if target is None:
            raise InvalidArgumentException(f"Node with ID {args[1]} does not exist!")
        attributes: dict[str, Any] = self.parse_attributes(args[2:], False)
        new_edge = Edge(source, target, attributes)
        self.graph.add_edge(new_edge)

    def clear(self):
        for edge in self.graph.get_edges():
            self.graph.remove_edge(edge.id)
        for node in self.graph.get_nodes():
            self.graph.remove_node(node.node_id)

    def delete_node(self, id: str):
        uuid: UUID = UUID(id)
        if self.graph.get_node(uuid) is None:
            raise InvalidArgumentException(f"Node with ID {id} does not exist!")
        self.graph.remove_node(uuid)

    def delete_edge(self, id: str):
        uuid: UUID = UUID(id)
        if self.graph.get_edge(uuid) is None:
            raise InvalidArgumentException(f"Edge with ID {id} does not exist!")
        self.graph.remove_edge(uuid)

    def update_node(self, args: list[str]):
        node: Node = self.graph.get_node(UUID(args[0]))
        if node is None:
            raise InvalidArgumentException(f"Node with ID {args[0]} does not exist!")
        attributes: dict[str, Any] = self.parse_attributes(args[1:], True)
        for key, value in attributes.items():
            if key in node.attributes and value is None:
                del node.attributes[key]
            else:
                node.attributes[key] = value

    def update_edge(self, args: list[str]):
        edge: Edge = self.graph.get_edge(UUID(args[0]))
        if edge is None:
            raise InvalidArgumentException(f"Edge with ID {args[0]} does not exist!")
        attributes: dict[str, Any] = self.parse_attributes(args[1:], True)
        for key, value in attributes.items():
            if key in edge.attributes and value is None:
                del edge.attributes[key]
            else:
                edge.attributes[key] = value