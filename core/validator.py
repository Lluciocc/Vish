# validator.py
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

from core.port_types import PortDirection, PortType


class GraphValidator:
    @staticmethod
    def is_valid_connection(graph, a, b) -> bool:
        if a is b:
            return False

        if a.port.node.id == b.port.node.id:
            return False

        if a.is_input == b.is_input:
            return False

        if not a.port.can_connect_to(b.port):
            return False

        if a.port.direction == PortDirection.OUTPUT:
            src_item = a
            dst_item = b
        else:
            src_item = b
            dst_item = a

        src = src_item.port
        dst = dst_item.port

        if GraphValidator._can_reach(graph, dst.node, src.node):
            return False


        is_exec = src.port_type == PortType.EXEC
        return True

    @staticmethod
    def _can_reach(graph, start_node, target_node) -> bool:
        visited = set()

        def dfs(node):
            if node.id in visited:
                return False
            visited.add(node.id)

            if node is target_node:
                return True

            for edge in graph.edges.values():
                if edge.source.node is node:
                    if dfs(edge.target.node):
                        return True
            return False

        return dfs(start_node)
