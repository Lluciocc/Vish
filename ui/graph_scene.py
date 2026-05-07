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

    def start_connection(self, first_port):
        if self.block_input:
            return

        self.block_input = True
        self.is_ctrl = False
        modifier = QApplication.keyboardModifiers()

        if first_port.edges:
            if modifier == Qt.ControlModifier: # Ctrl + LB
                self.is_ctrl = True
                for edge in first_port.edges:
                    self.drag_edges.append(edge)
                    self.pending_port = first_port
                    if first_port.is_input:
                        edge.target_port = edge.source_port
                    else:
                        edge.source_port = edge.target_port

            elif modifier == Qt.AltModifier: # Alt + LB
                for edge in first_port.edges:
                    self.drag_edges.append(edge)
                self.delete_edges()

            else: # LB
                if first_port.is_input or first_port.port.port_type == PortType.EXEC:
                    edge = first_port.edges[0]
                    if first_port.is_input:
                        self.pending_port = edge.source_port
                    else:
                        self.pending_port = edge.target_port
                    self.drag_edges.append(edge)
                    edge.target_port = edge.source_port
                    edge.source_port = first_port
                else:
                    self.new_edge(first_port)

        else:
            self.new_edge(first_port)

    def new_edge(self, first_port):
        drag_edge = self.initialize_edge(first_port)
        drag_edge.target_pos = first_port.center_scene_pos()
        drag_edge.update_positions()
        self.drag_edges.append(drag_edge)

    def initialize_edge(self, first_port):
        drag_edge = EdgeItem()
        drag_edge.source_port = first_port
        drag_edge.apply_style_from_source()
        self.addItem(drag_edge)
        return drag_edge

    def delete_edges(self): # Only edges in self.drag_edges become deleted!
        for edge in self.drag_edges:
            if edge.source_port:
                if edge.source_port.edges:
                    edge.source_port.edges.remove(edge)
            if edge.target_port:
                if edge.target_port.edges:
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
                if self.drag_edges[0].source_port and self.drag_edges[0].target_port:
                    for edge in self.drag_edges:
                        if self.pending_port.is_input and not self.is_ctrl:
                            edge.source_port = edge.target_port
                            edge.target_port = self.pending_port
                        elif not self.pending_port.is_input and not self.is_ctrl:
                            edge.target_port = edge.source_port
                            edge.source_port = self.pending_port
                        elif self.pending_port.is_input and self.is_ctrl:
                            edge.target_port = self.pending_port
                        else:
                            edge.source_port = self.pending_port

                        edge.update_positions()
                        self.is_ctrl = False
                    self.drag_edges.clear()
                    self.pending_port = None

            else:
                for edge in self.drag_edges:
                    self.removeItem(edge)
                self.drag_edges.clear()
                self.pending_port = None

    def switch_connections(self, first_port, second_port):
        if first_port.is_input == second_port.is_input and first_port.port.port_type == second_port.port.port_type:
            for edge in first_port.edges:
                self.pending_edges.append(edge)
            first_port.edges.clear()
            for edge in second_port.edges:
                first_port.edges.append(edge)
                if first_port.is_input:
                    edge.target_port = first_port
                else:
                    edge.source_port = first_port
                edge.update_positions()
                edge = self.graph.update_edge(edge.edge.id, edge.source_port.port, edge.target_port.port)

                if Config.DEBUG:
                    Logger.LogMessage(f"GRAPH.UPDATE_EDGE returned: {edge}")

            second_port.edges.clear()
            for edge in self.pending_edges:
                second_port.edges.append(edge)
                if first_port.is_input:
                    edge.target_port = second_port
                else:
                    edge.source_port = second_port
                edge.update_positions()
                edge = self.graph.update_edge(edge.edge.id, edge.source_port.port, edge.target_port.port)

                if Config.DEBUG:
                    Logger.LogMessage(f"GRAPH.UPDATE_EDGE returned: {edge}")

            self.pending_edges.clear()

            if Config.SYNC_NODES_AND_GEN:
                self.graph_changed.emit()
        else:
            self.restore_pending_connection()
                                                                    #TODO continue dragging the replaced edges
#    def keyReleaseEvent(self, event):
#        if not self.drag_edges:
#            return
#        if event.key() == Qt.Key_Control:
#            mouse_pos = self.views()[0].mapToScene(self.views()[0].mapFromGlobal(QCursor.pos()))
#            second_port = None
#            for item in self.items(mouse_pos):
#                if isinstance(item, PortItem):
#                    second_port = item
#                    break
#            if not second_port:
#                return
#            print("is port")
#            if not second_port.edges:
#                return
#            if self.pending_port == second_port:
#                return
#            else:
#                for edge in second_port.edges:
#                    self.pending_edges.append(edge)
#                for drag_edge in self.drag_edges:
#                    if second_port.edges:
#                        if drag_edge.target_port.is_input: edge
#                            if drag_edge.target_port.is_input == second_port.is_input:
#                                self.set_edge(drag_edge.source_port, second_port, drag_edge)
#                            else:
#                                self.set_edge(second_port, drag_edge.source_port, drag_edge)
#                        else:
#                            if drag_edge.target_port.is_input == second_port.is_input:
#                                self.set_edge(second_port, drag_edge.source_port, drag_edge)
#                            else:
#                                self.set_edge(drag_edge.source_port, second_port, drag_edge)
#                self.pending_port = second_port
#                self.drag_edges.clear()
#                print(self.pending_edges)
#                self.drag_edges = self.pending_edges

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
            self.restore_pending_connection()

        else:
            modifier = QApplication.keyboardModifiers()
            if second_port.edges:
                if modifier == Qt.AltModifier:          # Deleting previous edges (Alt)
                    if first_port.port.port_type == second_port.port.port_type:
                        self.pending_edges = self.drag_edges
                        self.drag_edges = second_port.edges
                        self.delete_edges()
                        self.drag_edges = self.pending_edges
                    else:
                        self.restore_pending_connection()


            if self.pending_port:                       # Check for self-connection on multi-dragging
                for drag_edge in self.drag_edges:
                    if drag_edge.source_port.port.node.id == second_port.port.node.id:
                        self.restore_pending_connection()
                        return

            if modifier == Qt.ControlModifier:          # Ctrl + LB:
                self.switch_connections(first_port, second_port)

            for drag_edge in self.drag_edges:
                if second_port.edges:
                    if modifier == Qt.ControlModifier:  # Ctrl + LB
                        continue

                    elif modifier == Qt.AltModifier:    # Alt + LB
                        if first_port.is_input == (first_port.is_input == second_port.is_input): # XNOR operator
                            self.set_edge(drag_edge.source_port, second_port, drag_edge)
                        else:
                            self.set_edge(second_port, drag_edge.source_port, drag_edge)

                    elif first_port.is_input:           # LB
                        self.restore_pending_connection()
                    else:                               # LB
                        if first_port.is_input == second_port.is_input:
                            if first_port.port.port_type == PortType.EXEC:
                                self.restore_pending_connection()
                            else:
                                self.set_edge(second_port, drag_edge.source_port, drag_edge)
                        else:
                            self.restore_pending_connection()

                else:                                   # LB, ignoring modifier
                    self.is_ctrl = False
                    if first_port.is_input == (first_port.is_input == second_port.is_input): # XNOR operator
                        self.set_edge(drag_edge.source_port, second_port, drag_edge)
                    else:
                        self.set_edge(second_port, drag_edge.source_port, drag_edge)
    #        for edge in self.drag_edges:
    #            print("test", edge.source_port.edges)
    #            print("test", edge.target_port.edges)
            self.drag_edges.clear()
            self.pending_port = None

    def set_edge(self, first_port, second_port, drag_edge):

        valid = self._is_valid_connection(first_port, second_port)
        if Config.DEBUG:
            Logger.LogMessage(f"Connection valid? {valid}")
        if not valid and not self.is_ctrl:
            if self.pending_port:
                self.restore_pending_connection()
            else:
                self._show_invalid_feedback(first_port, second_port)
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

        def commit():
            if Config.DEBUG:
                Logger.LogMessage(f"COMMIT: {first_port.port.port_type} -> {second_port.port.port_type}")

            edge = self.graph.add_edge(first_port.port, second_port.port)
            drag_edge.edge = edge

            if Config.DEBUG:
                Logger.LogMessage(f"GRAPH.ADD_EDGE returned: {edge}")

            if Config.SYNC_NODES_AND_GEN:
                self.graph_changed.emit()

        QTimer.singleShot(0, commit)

    def _is_valid_connection(self, a: PortItem, b: PortItem) -> bool:   #TODO still working?
        return GraphValidator.is_valid_connection(self.graph, a, b)

    def _show_invalid_feedback(self, a, b):                             #TODO still working?
        #Logger.Error("Invalid connection")
        edges = self.drag_edges
        if not edges:
            return

        for edge in edges:
            edge.setPen(QPen(QColor("#E74C3C"), 3))

        def cleanup():
            if edge.scene():
                self.removeItem(edge)
        self.drag_edges.clear()

        QTimer.singleShot(180, cleanup)

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

    def update_edges_for_node(self, node_item):
        for port_item in node_item.port_items.values():
            for edge in port_item.edges:
                edge.update_positions()

    def mouseMoveEvent(self, event):
        for drag_edge in self.drag_edges:
            drag_edge.set_target_pos(event.scenePos(), drag_edge.source_port.is_input)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.restore_pending_connection()

        super().mousePressEvent(event)
