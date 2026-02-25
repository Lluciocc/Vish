from core.port_types import PortType
from core.bash_context import BashContext
from nodes.registry import register_node
from .base_node import BaseNode

@register_node("set_variable", category="Variables", label="Set Variable", description="Sets a variable to a specific value")
class SetVariableNode(BaseNode):
    def __init__(self):
        super().__init__("set_variable", "Set Variable", "#F39C12")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Value", PortType.VARIABLE, "Value")
        self.add_output("Exec", PortType.EXEC, "Control flow output")

        self.properties["variable"] = "VAR"
        self.properties["value"] = ""

    def emit_bash(self, context: BashContext) -> str:
        var_name = self.properties.get("variable", "VAR")

        raw_value = self.properties.get("value", "")
        if raw_value.isdigit() or raw_value.startswith("$") or raw_value.startswith('"') or raw_value.startswith("'") or raw_value.startswith('`'):
            value_expr = raw_value
        else:
            value_expr = f'"{raw_value}"'


        value_port = self.inputs[1]
        if value_port.connected_edges:
            source_node = value_port.connected_edges[0].source.node

            emitted = source_node.emit_bash_value(context)
            if emitted is not None:
                value_expr = emitted

        context.variables[var_name] = value_expr
        return f'{var_name}={value_expr}'

@register_node("get_variable", category="Variables", label="Get Variable", description="Gets the value of a variable")
class GetVariableNode(BaseNode):
    def __init__(self):
        super().__init__("get_variable", "Get Variable", "#F39C12")
        self.add_output("Value", PortType.VARIABLE, "Variable value")
        self.properties["variable"] = "VAR"
    
    def emit_bash(self, context: BashContext) -> str:
        var_name = self.properties.get("variable", "VAR")
        return f"${var_name}"
    
    def emit_bash_value(self, context):
        return f"${self.properties['variable']}"

@register_node("file_exists", category="Variables", label="File Exists", description="Checks if a file exists")
class FileExistsNode(BaseNode):
    def __init__(self):
        super().__init__("file_exists", "File Exists", "#1ABC9C")
        self.add_input("Path", PortType.PATH, "File path")
        self.add_output("Result", PortType.CONDITION, "Existence check result")
        self.properties["path"] = ""
    
    def emit_bash(self, context: BashContext) -> str:
        path = self.properties.get("path", "")
        
        path_port = self.inputs[0]
        if path_port.connected_edges:
            source_node = path_port.connected_edges[0].source.node
            path = source_node.properties.get("value", path)
        
        return f'[ -f "{path}" ]'
    
@register_node("string_constant", category="Constants", label="String Constant", description="Represents a string constant value")
class StringConstantNode(BaseNode):
    def __init__(self):
        super().__init__("string_constant", "String Constant", "#BDC3C7")
        self.add_output("Value", PortType.STRING, "String value")
        self.properties["value"] = ""

    def emit_bash_value(self, context: BashContext) -> str:
        return f'"{self.properties.get("value", "")}"'