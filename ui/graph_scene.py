from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QCursor, QPen, QColor
from core.debug import Debug
from ui import edge_item
from ui.edge_item import EdgeItem
from ui.port_item import PortItem
from core.port_types import PortDirection
from core.validator import GraphValidator
from core.config import Config

class GraphScene(QGraphicsScene):
    node_selected = Signal(object)
    connection_created = Signal(object, object)
    graph_changed = Signal() 

    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.edges = []
        self.drag_edge = None
        self.start_port = None
        self.pending_port = None
        self.pending_scene_pos = None
        self.setBackgroundBrush(self.palette().dark())

    def start_connection(self, port_item):
        if port_item.is_input:
            for edge in list(self.edges):
                if edge.target_port is port_item:
                    if edge.edge:
                        self.graph.remove_edge(edge.edge.id)
                    if edge.scene() is self:
                        self.removeItem(edge)
                    self.edges.remove(edge)

        if self.drag_edge and self.drag_edge.scene() is self:
            self.removeItem(self.drag_edge)

        self.drag_edge = EdgeItem()
        self.drag_edge.source_port = port_item
        self.drag_edge.apply_style_from_source()
        self.addItem(self.drag_edge)

        pos = port_item.center_scene_pos()
        self.drag_edge.target_pos = pos
        self.drag_edge.update_positions()

    def end_connection(self, start_port_item):
        if not self.drag_edge:
            return

        mouse_pos = self.views()[0].mapToScene(
            self.views()[0].mapFromGlobal(QCursor.pos())
        )

        target_port = None
        for item in self.items(mouse_pos):
            if isinstance(item, PortItem) and item is not start_port_item:
                target_port = item
                break

        if target_port:
            self.finalize_connection(start_port_item, target_port)
        else:
            self.pending_port = start_port_item
            self.pending_scene_pos = mouse_pos
            self.views()[0].show_node_palette(mouse_pos)

    def finalize_connection(self, start_port, end_port):
        if not self.drag_edge:
            return

        if not self._is_valid_connection(start_port, end_port):
            self._show_invalid_feedback(start_port, end_port)
            return

        a = start_port.port
        b = end_port.port

        if a.direction == PortDirection.OUTPUT:
            source_item = start_port
            target_item = end_port
        else:
            source_item = end_port
            target_item = start_port

        if target_item.is_input:
            for edge in list(self.edges):
                if edge.target_port is target_item:
                    if edge.edge:
                        self.graph.remove_edge(edge.edge.id)
                    if edge.scene() is self:
                        self.removeItem(edge)
                    self.edges.remove(edge)

        edge_item = self.drag_edge
        edge_item.source_port = source_item
        edge_item.target_port = target_item
        edge_item.update_positions()

        self.drag_edge = None
        self.start_port = None
        self.pending_port = None
        self.pending_scene_pos = None

        def commit():
            edge = self.graph.add_edge(source_item.port, target_item.port)
            if edge:
                self.views()[0].add_edge_item(edge)
                if Config.SYNC_NODES_AND_GEN:
                    self.graph_changed.emit()
            if edge_item.scene() is self:
                self.removeItem(edge_item)

        QTimer.singleShot(0, commit)

    def _is_valid_connection(self, a: PortItem, b: PortItem) -> bool:
        return GraphValidator.is_valid_connection(
            self.graph,
            self.edges,
            a,
            b
        )

    def _cancel_drag_edge(self):
        if self.drag_edge:
            if self.drag_edge.scene() is self:
                self.removeItem(self.drag_edge)
        self.drag_edge = None
        self.start_port = None

    def _show_invalid_feedback(self, a, b):
        #Debug.Error("Invalid connection")
        edge = self.drag_edge
        if not edge:
            return

        edge.setPen(QPen(QColor("#E74C3C"), 3))

        def cleanup():
            if edge.scene():
                self.removeItem(edge)

        QTimer.singleShot(180, cleanup)
        self.drag_edge = None
        self.start_port = None

    def add_core_edge(self, core_edge, node_items):
        src_node_item = node_items[core_edge.source.node.id]
        tgt_node_item = node_items[core_edge.target.node.id]

        src_port_item = src_node_item.port_items[core_edge.source.id]
        tgt_port_item = tgt_node_item.port_items[core_edge.target.id]

        edge_item = EdgeItem(source_port=src_port_item, target_port=tgt_port_item)
        edge_item.edge = core_edge

        self.addItem(edge_item)
        edge_item.update_positions()
        self.edges.append(edge_item)

    def update_edges_for_node(self, node_item):
        for port_item in node_item.port_items.values():
            for edge in list(self.edges):
                if edge.source_port == port_item or edge.target_port == port_item:
                    edge.update_positions()

    def mouseMoveEvent(self, event):
        if self.drag_edge:
            self.drag_edge.set_target_pos(event.scenePos())
        super().mouseMoveEvent(event)
