from typing import List, Dict, Any
from .graph import Graph, Node, Port

class BashContext:
    def __init__(self):
        self.variables: Dict[str, str] = {}
        self.indent_level = 0
        self.lines: List[str] = []
        self.emitted_nodes = set()
    
    def add_line(self, line: str):
        indent = "    " * self.indent_level
        self.lines.append(f"{indent}{line}")
    
    def indent(self):
        self.indent_level += 1
    
    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)
    
    def get_script(self) -> str:
        return "\n".join(self.lines)

class BashEmitter:
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def emit(self) -> str:
        context = BashContext()
        context.add_line("#!/bin/bash")
        context.add_line("")
        context.add_line("# Generated from Visual Bash Editor (Vish)")
        context.add_line("")
        
        execution_order = self.graph.get_execution_order()
        
        for node in execution_order:
            if node.node_type == "start":
                continue

            if node.id in context.emitted_nodes:
                continue

            context.emitted_nodes.add(node.id)
            bash_code = node.emit_bash(context)
            if bash_code:
                context.add_line(bash_code)
        return context.get_script()