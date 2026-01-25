from core.port_types import PortType
from core.bash_context import BashContext
from .base_node import BaseNode
from nodes.registry import register_node

@register_node("to_string", category="Conversion", label="To String")
class ToString(BaseNode):
    def __init__(self):
        super().__init__("to_string", "To String", "#9B59B6")
        self.add_input("Input", PortType.INT, "Value to convert to string")
        self.add_output("Output", PortType.VARIABLE, "String representation")

    def emit_bash(self, context):
        input_port = self.inputs[0]

        if input_port.connected_edges:
            expr = input_port.connected_edges[0].source.node.emit_bash(context)
        else:
            expr = input_port.value or ""

        return f'"{expr}"'