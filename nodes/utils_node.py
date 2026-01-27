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

@register_node("to_int", category="Conversion", label="To Int")
class ToInt(BaseNode):
    def __init__(self):
        super().__init__("to_int", "To Int", "#9B59B6")
        self.add_input("Input", PortType.VARIABLE, "Value to convert to integer")
        self.add_output("Output", PortType.INT, "Integer representation")
        
    def emit_bash(self, context):
        input_port = self.inputs[0]

        if input_port.connected_edges:
            expr = input_port.connected_edges[0].source.node.emit_bash(context)
        else:
            expr = input_port.value or "0"

        return f'$(( {expr} ))'

@register_node("sleep", category="Utilities", label="Sleep", description="Pauses execution for a specified duration")
class SleepNode(BaseNode):
    def __init__(self):
        super().__init__("sleep", "Sleep", "#E67E22")
        self.add_input("Exec", PortType.EXEC)
        self.add_input("Duration", PortType.INT, "Duration to sleep in seconds")
        self.add_output("Exec", PortType.EXEC)
        self.properties["duration"] = 1

    def emit_bash(self, context: BashContext) -> str:
        duration = self.properties.get("duration", 1)

        duration_port = self.inputs[1]
        if duration_port.connected_edges:
            source_node = duration_port.connected_edges[0].source.node
            duration = source_node.properties.get("value", duration)

        return f'sleep {duration}'