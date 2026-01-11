from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QCursor
from ui.edge_item import EdgeItem
from ui.port_item import PortItem
from core.graph import Edge

class GraphScene(QGraphicsScene):
    node_selected = Signal(object)
    connection_created = Signal(object, object)

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
        self.drag_edge = EdgeItem()
        self.drag_edge.source_port = port_item
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
            self._cancel_drag_edge()
            self.views()[0].show_node_palette(mouse_pos)

    def finalize_connection(self, start_port, end_port):
        if not self._is_valid_connection(start_port, end_port):
            self._cancel_drag_edge()
            return

        source = start_port if not start_port.is_input else end_port
        target = end_port if source is start_port else start_port

        edge_item = self.drag_edge
        edge_item.source_port = source
        edge_item.target_port = target
        edge_item.update_positions()

        self.edges.append(edge_item)
        self.drag_edge = None
        self.start_port = None

        def commit_core_edge():
            core_edge = Edge(source=source.port, target=target.port)
            self.graph.edges.append(core_edge)
            edge_item.edge = core_edge

        QTimer.singleShot(0, commit_core_edge)

    def _is_valid_connection(self, a: PortItem, b: PortItem) -> bool:
        if a is b:
            return False
        if a.port.node.id == b.port.node.id:
            return False
        if a.is_input == b.is_input:
            return False

        source = a if not a.is_input else b
        target = b if source is a else a

        if source.port.port_type != target.port.port_type:
            return False

        for edge in self.edges:
            if edge.target_port is target:
                return False

        return True

    def _cancel_drag_edge(self):
        if self.drag_edge:
            self.removeItem(self.drag_edge)
            self.drag_edge = None
            self.start_port = None

    def add_core_edge(self, core_edge, node_items):
        src_node_item = node_items[core_edge.source.node.id]
        tgt_node_item = node_items[core_edge.target.node.id]

        src_port_item = src_node_item.port_items[core_edge.source.id]
        tgt_port_item = tgt_node_item.port_items[core_edge.target.id]

        edge_item = EdgeItem()
        edge_item.source_port = src_port_item
        edge_item.target_port = tgt_port_item
        edge_item.edge = core_edge

        self.addItem(edge_item)
        edge_item.update_positions()
        self.edges.append(edge_item)

    def update_edges_for_node(self, node_item):
        for port_item in node_item.port_items.values():
            for edge in self.edges:
                if edge.source_port == port_item or edge.target_port == port_item:
                    edge.update_positions()

    def mouseMoveEvent(self, event):
        if self.drag_edge:
            self.drag_edge.set_target_pos(event.scenePos())
        super().mouseMoveEvent(event)
