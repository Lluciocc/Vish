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
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_input("Duration", PortType.INT, "Duration to sleep in seconds")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["duration"] = 1

    def emit_bash(self, context: BashContext) -> str:
        duration = self.properties.get("duration", 1)

        duration_port = self.inputs[1]
        if duration_port.connected_edges:
            source_node = duration_port.connected_edges[0].source.node
            duration = source_node.properties.get("value", duration)

        return f'sleep {duration}'
    
@register_node("download_file", category="Utilities", label="Download File", description="Downloads a file from a specified URL")
class DownloadFileNode(BaseNode):
    def __init__(self):
        super().__init__("download_file", "Download File", "#1ABC9C")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["url"] = ""
        self.properties["output_path"] = ""

    def emit_bash(self, context: BashContext) -> str:
        url = self.properties.get("url", "")
        output_path = self.properties.get("output_path", "")

        return f'curl -o "{output_path}" "{url}"'

@register_node("git_clone", category="Utilities", label="Git Clone", description="Clones a Git repository to a specified destination")
class GitCloneNode(BaseNode):
    def __init__(self):
        super().__init__("git_clone", "Git Clone", "#3498DB")
        self.add_input("Exec", PortType.EXEC, "Control flow input")        
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["repo_url"] = ""
        self.properties["destination_path"] = ""

    def emit_bash(self, context: BashContext) -> str:
        repo_url = self.properties.get("repo_url", "")
        destination_path = self.properties.get("destination_path", "")

        return f'git clone "{repo_url}" "{destination_path}"'



@register_node("open_website", category="Utilities", label="Open Website", description="Opens a specified URL in the default web browser")  
class OpenWebsiteNode(BaseNode):
    def __init__(self):
        super().__init__("open_website", "Open Website", "#8E44AD")
        self.add_input("Exec", PortType.EXEC, "Control flow input")
        self.add_output("Exec", PortType.EXEC, "Control flow output")
        self.properties["url"] = ""

    def emit_bash(self, context: BashContext) -> str:
        url = self.properties.get("url", "")

        return f'xdg-open "{url}"'