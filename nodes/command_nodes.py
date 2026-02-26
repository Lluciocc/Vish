from core.port_types import PortType
from core.bash_context import BashContext
from .base_node import BaseNode
from nodes.registry import register_node

@register_node("run_command", category="Commands", label="Run a command", description="Executes a shell command")
class RunCommandNode(BaseNode):
    def __init__(self):
        super().__init__("run_command", "Run Command", "#2ECC71")
        self.add_input("Exec", PortType.EXEC)
        self.add_input("Command", PortType.STRING, "Command to run")
        self.add_output("Exec", PortType.EXEC)
        self.add_output("Output", PortType.STRING, "Command output")
        self.properties["command"] = "ls"
    
    def emit_bash(self, context: BashContext) -> str:
        command = self.properties.get("command", "")
        
        cmd_port = self.inputs[1]
        if cmd_port.connected_edges:
            source_node = cmd_port.connected_edges[0].source.node
            command = source_node.properties.get("value", command)
        
        return command

@register_node("pipe", category="Commands", label="Pipe", description="Pipes output from Command 1 into Command 2")
class PipeNode(BaseNode):
    def __init__(self):
        super().__init__("pipe", "Pipe", "#8E44AD")
        self.add_input("Exec", PortType.EXEC, "Execution Input")
        self.add_input("Command 1", PortType.STRING, "Left command")
        self.add_input("Command 2", PortType.STRING, "Right command")
        self.add_output("Exec", PortType.EXEC, "Execution Output")
        self.add_output("Output", PortType.STRING, "Output of piped command")
        self.properties["Command 1"] = "ls"
        self.properties["Command 2"] = "grep test"
        
    def emit_bash(self, context: BashContext) -> str:
        cmd1 = self.properties.get("Command 1", "ls")
        cmd2 = self.properties.get("Command 2", "")
        
        cmd1_port = self.inputs[1]
        if cmd1_port.connected_edges:
            source_node = cmd1_port.connected_edges[0].source.node
            cmd1 = source_node.properties.get("value", cmd1)
            
        cmd2_port = self.inputs[2]
        if cmd2_port.connected_edges:
            source_node = cmd2_port.connected_edges[0].source.node
            cmd2 = source_node.properties.get("value", cmd2)
            
        return f"{cmd1} | {cmd2}"

@register_node("echo", category="Commands", label="Print a text", description="Prints a text to the console")
class EchoNode(BaseNode):
    def __init__(self):
        super().__init__("echo", "Echo", "#3498DB")
        self.add_input("Exec", PortType.EXEC)
        self.add_input("Text", PortType.VARIABLE, "Things to print")
        self.add_output("Exec", PortType.EXEC)
        self.properties["text"] = "Hello"
        
    def emit_bash(self, context: BashContext) -> str:
        text = self.properties.get("text", "")

        text_port = self.inputs[1]

        if text_port.connected_edges:
            source_node = text_port.connected_edges[0].source.node

            value = source_node.emit_bash_value(context)
            if value is not None:
                text = value

        return f'echo "{text}"'

@register_node("exit", category="Commands", label="Exit script", description="Exits the script with a status code")
class ExitNode(BaseNode):
    def __init__(self):
        super().__init__("exit", "Exit", "#E74C3C")
        self.add_input("Exec", PortType.EXEC)
        self.add_input("Code", PortType.INT, "Exit code")
        self.properties["code"] = 0
    
    def emit_bash(self, context: BashContext) -> str:
        code = self.properties.get("code", 0)
        
        code_port = self.inputs[1]
        if code_port.connected_edges:
            source_node = code_port.connected_edges[0].source.node
            code = source_node.properties.get("value", code)
        
        return f"exit {code}"
