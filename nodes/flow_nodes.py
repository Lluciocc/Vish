from core.port_types import PortType
from core.bash_context import BashContext
from nodes.registry import register_node
from core.debug import Debug
from nodes.base_node import BaseNode

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
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Condition", PortType.CONDITION, "Condition to evaluate")
        self.add_output("True", PortType.EXEC, "If condition is true")
        self.add_output("False", PortType.EXEC, "If condition is false")
        self.add_output("Next", PortType.EXEC, "Continue after if")

    def emit_bash(self, context: BashContext) -> str:
        cond = self.inputs[1].get_condition(context)
        if not cond:
            Debug.Warn("If Node: No condition connected, skipping if statement.")
            return ""

        context.add_line(f"if {cond}; then")
        context.indent()
        self._emit_branch(context, 0)
        context.dedent()
        if self.outputs[1].connected_edges:
            context.add_line("else")
            context.indent()
            self._emit_branch(context, 1)
            context.dedent()

        context.add_line("fi")
        next_port = self.outputs[2]
        if next_port.connected_edges:
            BaseNode.emit_exec_chain(
                next_port.connected_edges[0].target.node,
                context
            )

        return ""

    def _emit_branch(self, context: BashContext, output_index: int):
        port = self.outputs[output_index]
        if not port.connected_edges:
            return
        BaseNode.emit_exec_chain(
            port.connected_edges[0].target.node,
            context
        )


@register_node("for", category="Flow", label="For Loop", description="Iterates over a list")
class ForNode(BaseNode):
    def __init__(self):
        super().__init__("for", "For Loop", "#9B59B6")

        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("List", PortType.STRING, "List to iterate over")

        self.add_output("Loop Body", PortType.EXEC, "Executed for each item")
        self.add_output("Item", PortType.VARIABLE, "Current item in the loop")
        self.add_output("Next", PortType.EXEC, "Continue after loop")

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
            start_node = body_port.connected_edges[0].target.node
            BaseNode.emit_exec_chain(start_node, context)

        context.dedent()
        context.add_line("done")

        next_port = self.outputs[2]
        if next_port.connected_edges:
            start_node = next_port.connected_edges[0].target.node
            BaseNode.emit_exec_chain(start_node, context)
        return ""
    
@register_node("while", category="Flow", label="While Loop", description="Repeats execution while a condition is true")
class WhileNode(BaseNode):
    def __init__(self):
        super().__init__("while", "While", "#8E44AD")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Condition", PortType.CONDITION, "Loop Condition")
        self.add_output("Body", PortType.EXEC, "Loop body")
        self.add_output("Next", PortType.EXEC, "Continue after loop")

    def emit_bash(self, context: BashContext) -> str:
        cond = self.inputs[1].get_condition(context)
        if not cond:
            Debug.Warn("While Node: No condition connected, skipping while loop.")
            return ""

        context.add_line(f"while {cond}; do")
        context.indent()

        body_port = self.outputs[0]
        if body_port.connected_edges:
            BaseNode.emit_exec_chain(
                body_port.connected_edges[0].target.node,
                context,
                stop_at=self
            )

        context.dedent()
        context.add_line("done")

        next_port = self.outputs[1]
        if next_port.connected_edges:
            BaseNode.emit_exec_chain(
                next_port.connected_edges[0].target.node,
                context
            )

        return ""

    def get_next_exec_node(self):
        return None
    
@register_node("function", category="Flow", label="Function", description="Defines a bash function")
class FunctionNode(BaseNode):
    def __init__(self):
        super().__init__("function", "Function", "#1ABC9C")
        self.add_output("Exec", PortType.EXEC, "Function body")

        self.properties["name"] = "my_function"

    def emit_bash(self, context: BashContext) -> str:
        name = self.properties.get("name", "my_function")
        context.add_function_line(f"{name}() {{") # double { to escape in f-string

        prev_buffer = context._current_buffer
        prev_indent = context.indent_level
        context._current_buffer = "function"
        context.indent_level = 1

        body_port = self.outputs[0]
        if body_port.connected_edges:
            start_node = body_port.connected_edges[0].target.node
            BaseNode.emit_exec_chain(start_node, context)
        context.indent_level = prev_indent
        context._current_buffer = prev_buffer

        context.add_function_line("}")
        context.add_function_line("")

        return ""

    
@register_node("call",category="Flow",label="Call Function",description="Calls a bash function")
class CallNode(BaseNode):
    def __init__(self):
        super().__init__("call", "Call", "#F39C12")

        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")

        self.properties["function"] = "my_function"

    def emit_bash(self, context: BashContext) -> str:
        return self.properties.get("function", "")
    
@register_node("return", category="Flow", label="Return", description="Return the result of a fonction")
class ReturnNode(BaseNode):
    def __init__(self):
        super().__init__("return", "Return", "#E74C3C")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Value", PortType.STRING, "Return value")

    def emit_bash(self, context):
        value = "0"
        val_port = self.inputs[1]
        if val_port.connected_edges:
            src = val_port.connected_edges[0].source.node
            value = src.properties.get("value", value)
        return f"return {value}"