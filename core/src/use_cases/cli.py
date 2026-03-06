from datetime import datetime
from typing import Any
from uuid import UUID

from api.model import Graph, Node, Edge

class InvalidArgumentException(Exception):
    pass

class CLI(object):
    """
    Object encapsulating the CLI functionalities.

    Those functionalities include:
    - command parsing
    - graph manipulation
    - query argument passing
    """

    @staticmethod
    def parse_command(graph: Graph, command: str):
        """
        Parses the command abd performs the graph action based on it

        Throws InvalidArgumentException if the command is invalid
        """
        parsed = command.split(' ')
        match parsed[0]:
            case 'create-node':
                return CLI.create_node(graph, parsed[1:])
            case 'create-edge':
                return CLI.create_edge(graph, parsed[1:])
            case 'update-node':
                return CLI.update_node(graph, parsed[1:])
            case 'update-edge':
                return CLI.update_edge(graph, parsed[1:])
            case 'delete-node':
                if len(parsed) != 2:
                    raise InvalidArgumentException("delete-node takes one argument!")
                return CLI.delete_node(graph, parsed[1])
            case 'delete-edge':
                if len(parsed) != 3:
                    raise InvalidArgumentException("delete-edge takes two arguments!")
                return CLI.delete_edge(graph, parsed[1], parsed[2])
            case 'search':
                if len(parsed) != 2:
                    raise InvalidArgumentException("search takes one argument!")
                return parsed[1]
            case 'filter':
                if len(parsed) < 3:
                    raise InvalidArgumentException("Improper filter expression format!")
                return command.split(' ', maxsplit=1)
            case 'clear-graph':
                CLI.clear(graph)
                return "Graph cleared!"
            case _:
                raise InvalidArgumentException(f'Unknown command: {parsed[0]}')

    @staticmethod
    def parse_attributes(args: list[str], update: bool) -> dict[str, Any]:
        """
        Parses the attributes of create- and update- commands

        Every attribute is of the form [name]=[value] and is preceded by a flag describing its data type
        Possible flags are: --int, --float, --string, and --date
        NOTE: Dates are accepted in the DD.MM.YYYY format
        """
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

    @staticmethod
    def create_node(graph: Graph, args: list[str]) -> Node:
        """
        Creates a new node with given attributes
        Returns the newly created node
        """
        attributes: dict[str, Any] = CLI.parse_attributes(args, False)
        new_node = Node()
        new_node.set_attributes(attributes)
        graph.add_node(new_node)
        return new_node

    @staticmethod
    def create_edge(graph: Graph, args: list[str]) -> Edge:
        """
        Creates a new edge with given attributes
        Returns the newly created edge
        """
        source: Node = graph.get_node(UUID(args[0]))
        target: Node = graph.get_node(UUID(args[1]))
        if source is None:
            raise InvalidArgumentException(f"Node with ID {args[0]} does not exist!")
        if target is None:
            raise InvalidArgumentException(f"Node with ID {args[1]} does not exist!")
        attributes: dict[str, Any] = CLI.parse_attributes(args[2:], False)
        new_edge = Edge(source, target)
        new_edge.set_attributes(attributes)
        graph.add_edge(new_edge)
        return new_edge

    def clear(graph: Graph):
        """
        Clears the graph
        """
        for edge in list(graph.get_edges()):
            graph.remove_edge(edge.id)
        for node in list(graph.get_nodes()):
            graph.remove_node(node.id)

    @staticmethod
    def delete_node(graph: Graph, id: str):
        """
        Deletes a node given its ID
        No return value
        """
        uuid: UUID = UUID(id)
        if graph.get_node(uuid) is None:
            raise InvalidArgumentException(f"Node with ID {id} does not exist!")
        graph.remove_node(uuid)

    @staticmethod
    def delete_edge(graph: Graph, source_id: str, target_id: str):
        """
        Deletes an edge given its source and target node IDs
        No return value
        """
        source_uuid: UUID = UUID(source_id)
        target_uuid: UUID = UUID(target_id)
        edge: Edge = graph.get_edge_between(source_uuid, target_uuid)
        if edge is None:
            raise InvalidArgumentException(f"Edge {source_id} - {target_id} does not exist!")
        graph.remove_edge(edge.id)

    @staticmethod
    def update_node(graph: Graph, args: list[str]) -> Node:
        """
        Updates the node given its ID
        Returns the updated node
        """
        node: Node = graph.get_node(UUID(args[0]))
        if node is None:
            raise InvalidArgumentException(f"Node with ID {args[0]} does not exist!")
        attributes: dict[str, Any] = CLI.parse_attributes(args[1:], True)
        for key, value in attributes.items():
            if key in node.attributes and value is None:
                del node.attributes[key]
            else:
                node.attributes[key] = value
        return node

    @staticmethod
    def update_edge(graph: Graph, args: list[str]) -> Edge:
        """
        Updates the edge given its ID
        Returns the updated edge
        """
        edge: Edge = graph.get_edge(UUID(args[0]))
        if edge is None:
            raise InvalidArgumentException(f"Edge with ID {args[0]} does not exist!")
        attributes: dict[str, Any] = CLI.parse_attributes(args[1:], True)
        for key, value in attributes.items():
            if key in edge.attributes and value is None:
                del edge.attributes[key]
            else:
                edge.attributes[key] = value
        return edge