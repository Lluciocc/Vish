from typing import List, Optional, Dict, Any
from uuid import uuid4
from .port_types import PortType, PortDirection

class Port:
    def __init__(self, name: str, port_type: PortType, direction: PortDirection, node: 'Node', tooltip=""):
        self.id = str(uuid4())
        self.name = name
        self.port_type = port_type
        self.direction = direction
        self.node = node
        self.value: Any = None
        self.connected_edges: List['Edge'] = []
        self.tooltip = tooltip
    
    def can_connect_to(self, other: 'Port') -> bool:
        if self.direction == other.direction:
            return False
        if self.port_type == PortType.EXEC and other.port_type == PortType.EXEC:
            return True
        return self.port_type == other.port_type
    
    def is_connected(self) -> bool:
        return len(self.connected_edges) > 0

class Node:
    def __init__(self, node_type: str, title: str):
        self.id = str(uuid4())
        self.node_type = node_type
        self.title = title
        self.inputs: List[Port] = []
        self.outputs: List[Port] = []
        self.x = 0.0
        self.y = 0.0
        self.properties: Dict[str, Any] = {}
    
    def add_input(self, name: str, port_type: PortType, tooltip="") -> Port:
        port = Port(name, port_type, PortDirection.INPUT, self, tooltip)
        self.inputs.append(port)
        return port
    
    def add_output(self, name: str, port_type: PortType, tooltip="") -> Port:
        port = Port(name, port_type, PortDirection.OUTPUT, self, tooltip)
        self.outputs.append(port)
        return port
    
    def get_exec_output(self) -> Optional[Port]:
        for port in self.outputs:
            if port.port_type == PortType.EXEC:
                return port
        return None
    
    def get_exec_input(self) -> Optional[Port]:
        for port in self.inputs:
            if port.port_type == PortType.EXEC:
                return port
        return None
    
    def emit_bash(self, context: 'BashContext') -> str:
        return ""

class Edge:
    def __init__(self, source: Port, target: Port):
        self.id = str(uuid4())
        self.source = source
        self.target = target
        source.connected_edges.append(self)
        target.connected_edges.append(self)
    
    def disconnect(self):
        self.source.connected_edges.remove(self)
        self.target.connected_edges.remove(self)

class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
    
    def add_node(self, node: Node):
        self.nodes[node.id] = node
    
    def remove_node(self, node_id: str):
        if node_id in self.nodes:
            node = self.nodes[node_id]
            for port in node.inputs + node.outputs:
                for edge in port.connected_edges[:]:
                    self.remove_edge(edge.id)
            del self.nodes[node_id]
    
    def add_edge(self, source: Port, target: Port) -> Optional[Edge]:
        if not source.can_connect_to(target):
            return None
        edge = Edge(source, target)
        self.edges[edge.id] = edge
        return edge
    
    def remove_edge(self, edge_id: str):
        if edge_id in self.edges:
            edge = self.edges[edge_id]
            edge.disconnect()
            del self.edges[edge_id]
    
    def get_start_node(self) -> Optional[Node]:
        for node in self.nodes.values():
            if node.node_type == "start":
                return node
        return None
    
    def get_execution_order(self):
        from core.port_types import PortType

        visited = set()
        ordered = []
        start = None
        for node in self.nodes.values():
            if node.node_type == "start":
                start = node
                break

        if not start:
            return []

        def walk(node):
            if node.id in visited:
                return
            visited.add(node.id)
            ordered.append(node)
            for output in node.outputs:
                if output.port_type != PortType.EXEC:
                    continue

                for edge in output.connected_edges:
                    next_node = edge.target.node
                    walk(next_node)

        walk(start)
        return ordered
