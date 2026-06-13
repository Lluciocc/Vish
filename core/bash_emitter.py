# bash_emitter.py
#
# Copyright 2026 Lluciocc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

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
