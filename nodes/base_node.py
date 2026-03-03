from abc import abstractmethod
from core.graph import Node, PortType
from core.bash_context import BashContext
from core.node_color import NodeColor
from core.debug import Debug

class BaseNode(Node):
    def __init__(self, node_type: str, title: str):
        super().__init__(node_type, title)
        color = NodeColor.get_color(node_type)
        if not color:
            color = "#9d9d9d"
            Debug.Warn(f"no color for node type '{node_type}' found.")
        self.color = color
    
    @abstractmethod
    def emit_bash(self, context: BashContext) -> str:
        pass

    def emit_bash_value(self, context):
        return None
    
    def emit_condition(self, context):
        return None

    def get_next_exec_node(self):
        exec_outputs = [
            o for o in self.outputs
            if o.port_type == PortType.EXEC and o.connected_edges
        ]
        if not exec_outputs:
            return None

        return exec_outputs[0].connected_edges[0].target.node
    
    @staticmethod
    def emit_exec_chain(start_node, context, stop_at=None):
        current = start_node
        while current:
            if current.id in context.emitted_nodes:
                break

            context.emitted_nodes.add(current.id)

            bash = current.emit_bash(context)
            if bash:
                context.add_line(bash)

            if current == stop_at:
                break

            current = current.get_next_exec_node()