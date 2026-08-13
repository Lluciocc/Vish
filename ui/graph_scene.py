# graph_scene.py
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
from core.port_types import PortDirection, PortType
from core.validator import GraphValidator
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QPen
from PySide6.QtWidgets import QApplication, QGraphicsScene
from ui import edge_item
from ui.edge_item import EdgeItem
from ui.port_item import PortItem


class GraphScene(QGraphicsScene):                                          #TODO Add undo commands
    node_selected = Signal(object)
    connection_created = Signal(object, object)
    graph_changed = Signal()
    auto_save_triggered = Signal()

    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.drag_edges = []
        self.pending_port = None
        self.pending_edges = []
        self._z_counter = 2
        self.setBackgroundBrush(self.palette().dark())
        self.block_input = False
        self.is_ctrl = False
        self.edge_logger_counter = "+1"

    def start_connection(self, first_port):
        if self.block_input:
            return

        self.block_input = True
        self.is_ctrl = False
        modifier = QApplication.keyboardModifiers()

        if first_port.edges:
            match modifier:
                case Qt.ControlModifier:    # Ctrl + LB
                    self.is_ctrl = True
                    for edge in first_port.edges:
                        self.drag_edges.append(edge)
                        self.pending_port = first_port
                        if first_port.is_input:
                            edge.target_port = edge.source_port
                        else:
                            edge.source_port = edge.target_port
                    self.colorize_port(first_port, True)
                    if Config.DEBUG:
                        Logger.LogMessage("-SCENE.START_CONNECTION: grab edge")

                case Qt.AltModifier:        # Alt + LB
                    for edge in first_port.edges:
                        self.drag_edges.append(edge)
                    if Config.DEBUG:
                        Logger.LogMessage("-SCENE.START_CONNECTION: delete edge")
                        Logger.LogMessage(f"EDGES: {len(self.graph.edges) - len(self.drag_edges)} (-{len(self.drag_edges)})")
                    self.delete_edges()

                case _:                     # LB
                    if first_port.is_input or first_port.port.port_type == PortType.EXEC:
                        edge = first_port.edges[0]
                        if first_port.is_input:
                            self.pending_port = edge.source_port
                        else:
                            self.pending_port = edge.target_port
                        self.drag_edges.append(edge)
                        edge.target_port = edge.source_port
                        edge.source_port = first_port
                        if Config.DEBUG:
                            Logger.LogMessage("-SCENE.START_CONNECTION: renew edge")
                            self.edge_logger_counter = "+/-0"
                    else:
                        self.new_edge(first_port)

        else:
            self.new_edge(first_port)

    def new_edge(self, first_port):
        drag_edge = self.initialize_edge(first_port)
        drag_edge.target_pos = first_port.center_scene_pos()
        drag_edge.update_positions()
        self.drag_edges.append(drag_edge)
        if Config.DEBUG:
            Logger.LogMessage("-SCENE.START_CONNECTION: new edge")

    def initialize_edge(self, first_port):
        drag_edge = EdgeItem()
        drag_edge.source_port = first_port
        drag_edge.apply_style_from_source()
        self.addItem(drag_edge)
        return drag_edge

    def delete_edges(self): # Only edges in self.drag_edges become deleted!
        if Config.DEBUG:
            Logger.LogMessage(f"SCENE.DELETE_EDGES: delete edges (-{len(self.drag_edges)})")

        for edge in self.drag_edges:
            if edge.source_port:
                if edge.source_port.edges:
                    if edge in edge.source_port.edges:
                        self.colorize_port(edge.source_port, True)
                        edge.source_port.edges.remove(edge)
            if edge.target_port:
                if edge.target_port.edges:
                    if edge in edge.target_port.edges:
                        self.colorize_port(edge.target_port, True)
                        edge.target_port.edges.remove(edge)
            if edge.edge:
                self.graph.remove_edge(edge.edge.id)
            self.removeItem(edge)
        self.drag_edges.clear()

        if Config.SYNC_NODES_AND_GEN:
            self.graph_changed.emit()

    def remove_pending_port(self, edge):
        if self.pending_port:
            self.graph.remove_edge(edge.edge.id)
            self.pending_port.edges.remove(edge)

    def restore_pending_connection(self):
        if self.drag_edges:
            if self.pending_port:
                if Config.DEBUG:
                    Logger.LogMessage(f"SCENE.RESTORE_PENDING_CONNECTION: restore drag_edges, {self.drag_edges}")

                if self.drag_edges[0].source_port and self.drag_edges[0].target_port:
                    self._show_invalid_feedback()

            else:
                if Config.DEBUG:
                    Logger.LogMessage(f"SCENE.RESTORE_PENDING_CONNECTION: delete drag_edges, {self.drag_edges}")
                self._show_invalid_feedback()

    def switch_connections(self, first_port, second_port, backswitch: bool):
        if first_port.is_input == second_port.is_input:
            valid = GraphValidator.is_valid_port_type(first_port.edges, second_port)
            if valid:
                valid = GraphValidator.is_valid_port_type(self.pending_port.edges, first_port)
            if valid:
                if Config.DEBUG:
                    if backswitch:
                        Logger.LogMessage(f"SCENE.SWITCH_CONNECTIONS: {first_port} <-> {second_port}")
                    else:
                        Logger.LogMessage(f"SCENE.SWITCH_CONNECTIONS: {first_port} -> {second_port}")

                for edge in first_port.edges:
                    self.pending_edges.append(edge)
                first_port.edges.clear()
                if backswitch:
                    for edge in second_port.edges:
                        first_port.edges.append(edge)
                        if first_port.is_input:
                            edge.target_port = first_port
                        else:
                            edge.source_port = first_port
                        edge.update_positions()
                        self.graph.update_edge(edge.edge.id, edge.source_port.port, edge.target_port.port)

                    second_port.edges.clear()
                for edge in self.pending_edges:
                    second_port.edges.append(edge)
                    if first_port.is_input:
                        edge.target_port = second_port
                    else:
                        edge.source_port = second_port
                    edge.update_positions()
                    self.graph.update_edge(edge.edge.id, edge.source_port.port, edge.target_port.port)

                self.colorize_port(first_port, False)
                self.colorize_port(second_port, False)
                self.pending_edges.clear()

                if Config.SYNC_NODES_AND_GEN:
                    self.graph_changed.emit()
            else:
                self.restore_pending_connection()

    def end_connection(self, first_port):
        if not self.drag_edges:
            return

        mouse_pos = self.views()[0].mapToScene(self.views()[0].mapFromGlobal(QCursor.pos()))
        second_port = None
        for item in self.items(mouse_pos):
            if isinstance(item, PortItem):
                second_port = item
                break
        if not second_port:
            self.views()[0].show_node_palette(mouse_pos)
            return

        if first_port == second_port:
            if second_port.edges:
                if Config.DEBUG:
                    GraphValidator.is_valid_connection(self.graph, first_port, second_port)
                self._show_invalid_feedback()
                self.restore_pending_connection()
                return
            else:
                self.views()[0].show_node_palette(mouse_pos)
                return

        modifier = QApplication.keyboardModifiers()
        if second_port.edges:
            if modifier == Qt.AltModifier:          # Deleting previous edges (Alt)
                if Config.DEBUG:
                    Logger.LogMessage("SCENE.END_CONNECTION: delete previous drag_edges")
                if first_port.port.port_type == second_port.port.port_type:
                    self.pending_edges.clear()
                    for edge in self.drag_edges:
                        self.pending_edges.append(edge)
                    self.drag_edges.clear()
                    for edge in second_port.edges:
                        self.drag_edges.append(edge)
                    if Config.DEBUG:
                        self.edge_logger_counter = f"-{len(self.drag_edges)}"
                    self.delete_edges()
                    for edge in self.pending_edges:
                        self.drag_edges.append(edge)
                    self.pending_edges.clear()
                else:
                    self.restore_pending_connection()

        if self.pending_port:                       # Check for self-connection on multi-dragging
            for drag_edge in self.drag_edges:
                if drag_edge.source_port.port.node.id == second_port.port.node.id:
                    self.restore_pending_connection()
                    return

        if modifier == Qt.ControlModifier:          # Ctrl + LB:
            if Config.DEBUG:
                Logger.LogMessage("SCENE.END_CONNECTION: switch connections")
            self.switch_connections(first_port, second_port, True)

        elif self.is_ctrl:                          # LB after Ctrl + LB start_connection
            match (second_port.is_input, second_port.edges, second_port.port.port_type == PortType.EXEC):
                case (True, [], _) | (False, _, False) | (_, [], True):
                    if Config.DEBUG:
                        Logger.LogMessage("SCENE.END_CONNECTION: switch connections with empty port")
                    self.switch_connections(first_port, second_port, False)
                case _:
                    self.restore_pending_connection()
                    return

        for drag_edge in self.drag_edges:
            if second_port.edges:
                if self.is_ctrl:                    # Ctrl + LB
                    continue

                elif first_port.is_input and first_port.port.port_type == PortType.EXEC:           # LB
                    self.restore_pending_connection()
                else:                               # LB
                    if first_port.is_input == second_port.is_input:
                        if first_port.port.port_type == PortType.EXEC:
                            self.restore_pending_connection()
                        else:
                            self.set_edge(second_port, drag_edge.source_port, drag_edge)
                    else:
                        if first_port.port.port_type == PortType.EXEC or second_port.is_input:
                            self.restore_pending_connection()
                        else:
                            self.set_edge(second_port, drag_edge.source_port, drag_edge)

            else:                                   # LB, ignoring modifier
                if self.is_ctrl:
                    self.is_ctrl = False
                    if Config.DEBUG:
                        self.edge_logger_counter = None
                if first_port.is_input == (first_port.is_input == second_port.is_input): # XNOR operator
                    self.set_edge(drag_edge.source_port, second_port, drag_edge)
                else:
                    self.set_edge(second_port, drag_edge.source_port, drag_edge)

        self.drag_edges.clear()
        self.pending_port = None
        if Config.DEBUG:
            self.edge_logger_counter = "+1"

    def set_edge(self, first_port, second_port, drag_edge):

        valid = GraphValidator.is_valid_connection(self.graph, first_port, second_port)
        if not valid and not self.is_ctrl:
            if self.pending_port:
                self.restore_pending_connection()
            else:
                self._show_invalid_feedback()
            return

        if not drag_edge:
            drag_edge = self.initialize_edge(first_port)

        if self.pending_port:
            if self.pending_port.is_input:
                second_port.edges.append(drag_edge)
            else:
                first_port.edges.append(drag_edge)
            self.remove_pending_port(drag_edge)
        else:
            first_port.edges.append(drag_edge)
            second_port.edges.append(drag_edge)
        drag_edge.source_port = first_port
        drag_edge.target_port = second_port
        drag_edge.update_positions()

        if second_port.port.port_type == PortType.ANY:
            drag_edge.overwrite_color(first_port.port.port_type)

        edge = self.graph.add_edge(first_port.port, second_port.port)
        drag_edge.edge = edge

        if second_port.port.port_type == PortType.ANY:
            self.colorize_port(second_port, False)

        if Config.DEBUG:
            Logger.LogMessage(f"SCENE.SET_EDGE: {first_port.port.port_type} -> {second_port.port.port_type}")
            Logger.LogMessage(f"SCENE.SET_EDGE: {edge}")
            if self.edge_logger_counter:
                Logger.LogMessage(f"EDGES: {len(self.graph.edges)} ({self.edge_logger_counter})")

        if Config.SYNC_NODES_AND_GEN:
            self.graph_changed.emit()


    def _show_invalid_feedback(self):
        if not self.drag_edges:
            return
        edge0 = self.drag_edges[0]

        if self.pending_port:
            edges = []
            for edge in self.drag_edges:
                if edge0.source_port == edge0.target_port:
                    edge.source_port.overwrite_color("invalid")
                edge.overwrite_color("invalid")
                edges.append(edge)
            port = self.pending_port
            is_ctrl = self.is_ctrl

            self.is_ctrl = False
            self.drag_edges.clear()
            self.pending_port = None

            def restore_edges():
                for edge in edges:
                    edge.source_port.overwrite_color(None)
                    match (port.is_input, is_ctrl):
                        case (True, False):
                            edge.source_port = edge.target_port
                            edge.target_port = port
                        case (False, False):
                            edge.target_port = edge.source_port
                            edge.source_port = port
                        case (True, True):
                            edge.target_port = port
                        case (False, True):
                            edge.source_port = port
                    edge.overwrite_color(None)
                    edge.update_positions()
                self.colorize_port(edges[0].source_port, False)
                self.colorize_port(edges[0].target_port, False)

            QTimer.singleShot(180, restore_edges)


        elif not edge0.target_port or edge0.source_port != edge0.target_port:
            edges = []
            for edge in self.drag_edges:
                edge.overwrite_color("invalid")
                edges.append(edge)

            def cleanup_edge():
                for edge in edges:
                    self.drag_edges.append(edge)
                self.delete_edges()

            QTimer.singleShot(180, cleanup_edge)

        else:
            if Config.DEBUG:
                Logger.LogWarning("SCENE._SHOW_INVALID: missing feedback")

    def colorize_port(self, colorize_port, reset):
        if reset:
            colorize_port.overwrite_color("reset")

        elif colorize_port.port.port_type == PortType.ANY:
            if colorize_port.edges:
                color = colorize_port.edges[0].get_default_style().color
                colorize_port.overwrite_color(color)

    def add_core_edge(self, core_edge, node_items):

        source_node_item = node_items[core_edge.source.node.id]
        target_node_item = node_items[core_edge.target.node.id]

        source_port_item = source_node_item.port_items[core_edge.source.id]
        target_port_item = target_node_item.port_items[core_edge.target.id]

        edge_item = EdgeItem(source_port=source_port_item, target_port=target_port_item)
        edge_item.edge = core_edge

        source_port_item.edges.append(edge_item)
        target_port_item.edges.append(edge_item)

        self.addItem(edge_item)
        edge_item.update_positions()

        self.colorize_port(source_port_item, False)
        self.colorize_port(target_port_item, False)

    def update_edges_for_node(self, node_item):
        for port_item in node_item.port_items.values():
            for edge in port_item.edges:
                edge.update_positions()

    def mouseMoveEvent(self, event):
        for drag_edge in self.drag_edges:
            drag_edge.set_target_pos(event.scenePos(), drag_edge.source_port.is_input)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton and self.drag_edges:
            if Config.DEBUG:
                Logger.LogMessage("SCENE.RightButton: cancel dragging")
            self.restore_pending_connection()
            self.drag_edges.clear()

        super().mousePressEvent(event)
