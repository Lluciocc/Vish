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

from core.config import Config
from core.logger import Logger
from core.port_types import PortDirection


class GraphValidator:
    @staticmethod
    def is_valid_connection(graph, a, b) -> bool:
        if a is b:
            if Config.DEBUG:
                Logger.LogMessage("VALIDATOR: invalid, port self connection")
            return False

        if a.port.node.id == b.port.node.id:
            if Config.DEBUG:
                Logger.LogMessage("VALIDATOR: invalid, node self connection")
            return False

        if a.is_input == b.is_input:
            if Config.DEBUG:
                if a.is_input:
                    Logger.LogMessage("VALIDATOR: invalid, both input port")
                else:
                    Logger.LogMessage("VALIDATOR: invalid, both output port")
            return False

        if not a.port.can_connect_to(b.port):
            if Config.DEBUG:
                Logger.LogMessage(f"VALIDATOR: invalid, {a.port.port_type} -> {b.port.port_type}")
            return False

        if a.port.direction == PortDirection.OUTPUT:
            source_item = a
            target_item = b
        else:
            source_item = b
            target_item = a

        source = source_item.port
        target = target_item.port

        if GraphValidator._can_reach(graph, target.node, source.node):
            if Config.DEBUG:
                Logger.LogMessage("VALIDATOR: invalid -> cannot reach")
            return False

        if Config.DEBUG:
            Logger.LogMessage("VALIDATOR: valid")
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

    @staticmethod
    def is_valid_port_type(drag_edges, target_port) -> bool:
        for edge in drag_edges:
            if not edge.source_port.port.can_connect_to(target_port.port):
                if Config.DEBUG:
                    Logger.LogMessage(f"VALIDATOR: invalid, {edge.source_port.port.port_type} -> {target_port.port.port_type}")
                return False
        return True
