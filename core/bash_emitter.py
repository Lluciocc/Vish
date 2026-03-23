from core.graph import Graph
from nodes.base_node import BaseNode
from core.bash_context import BashContext
from core.config import Config

class BashEmitter:
    def __init__(self, graph: Graph):
        self.graph = graph

    def emit(self) -> str:
        context = BashContext()

        header = [
            "#!/bin/bash/env bash",
            "",
            "# Generated with Visual Bash Editor",
            "",
            ""
        ]
        if Config.CUSTOM_SHEBANG:
            header[0] = Config.CUSTOM_SHEBANG
        for node in self.graph.nodes.values():
            if node.node_type == "function":
                if node.id in context.emitted_nodes:
                    continue
                context.emitted_nodes.add(node.id)
                node.emit_bash(context)
        start_node = self.graph.get_start_node()
        if start_node and start_node.outputs and start_node.outputs[0].connected_edges:
            first = start_node.outputs[0].connected_edges[0].target.node
            BaseNode.emit_exec_chain(first, context)
        return "\n".join(header) + context.get_script()
