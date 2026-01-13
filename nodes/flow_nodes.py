from core.port_types import PortType
from core.bash_emitter import BashContext
from nodes.registry import register_node
from .base_node import BaseNode

@register_node("start", category="Flow", label="Start", description="The starting point of the flow")
class StartNode(BaseNode):
    def __init__(self):
        super().__init__("start", "Start", "#4A90E2")
        self.add_output("Exec", PortType.EXEC, "Start of the flow")
    
    def emit_bash(self, context: BashContext) -> str:
        return ""

@register_node("if", category="Flow", label="If Condition", description="Evaluates a condition and branches the flow")
class IfNode(BaseNode):
    def __init__(self):
        super().__init__("if", "If", "#E94B3C")
        self.add_input("Exec", PortType.EXEC)
        self.add_input("Condition", PortType.STRING, "Must be a string")
        self.add_output("True", PortType.EXEC, "If condition is true")
        self.add_output("False", PortType.EXEC, "If condition is false")
        self.properties["condition"] = ""
    
    def emit_bash(self, context: BashContext) -> str:
        condition = self.properties.get("condition", "")
        
        condition_port = self.inputs[1]
        if condition_port.connected_edges:
            source_node = condition_port.connected_edges[0].source.node
            condition = source_node.properties.get("value", condition)
        
        context.add_line(f"if [ {condition} ]; then")
        context.indent()
        
        true_port = self.outputs[0]
        if true_port.connected_edges:
            next_node = true_port.connected_edges[0].target.node
            bash = next_node.emit_bash(context)
            if bash:
                context.add_line(bash)
        
        context.dedent()
        
        false_port = self.outputs[1]
        if false_port.connected_edges:
            context.add_line("else")
            context.indent()
            next_node = false_port.connected_edges[0].target.node
            bash = next_node.emit_bash(context)
            if bash:
                context.add_line(bash)
            context.dedent()
        
        context.add_line("fi")
        return ""

@register_node("for", category="Flow", label="For Loop", description="Iterates over a list")
class ForNode(BaseNode):
    def __init__(self):
        super().__init__("for", "For Loop", "#9B59B6")
        self.add_input("Exec", PortType.EXEC)
        self.add_input("List", PortType.STRING, "List to iterate over")
        self.add_output("Loop Body", PortType.EXEC)
        self.add_output("Item", PortType.VARIABLE, "Current item in the loop")
        self.properties["variable"] = "item"
    
    def emit_bash(self, context: BashContext) -> str:
        var_name = self.properties.get("variable", "item")
        list_expr = self.properties.get("list", "*")
        
        list_port = self.inputs[1]
        if list_port.connected_edges:
            source_node = list_port.connected_edges[0].source.node
            list_expr = source_node.properties.get("value", list_expr)
        
        context.add_line(f"for {var_name} in {list_expr}; do")
        context.indent()
        
        body_port = self.outputs[0]
        if body_port.connected_edges:
            next_node = body_port.connected_edges[0].target.node
            bash = next_node.emit_bash(context)
            if bash:
                context.add_line(bash)
        
        context.dedent()
        context.add_line("done")
        return ""