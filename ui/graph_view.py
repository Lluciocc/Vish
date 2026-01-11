from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPainter
from core.graph import Graph, Port
from ui.palette import NodePalette
from .graph_scene import GraphScene
from .node_item import NodeItem
from .edge_item import EdgeItem

class GraphView(QGraphicsView):
    connection_request = Signal(Port, Port)
    
    def __init__(self, graph, editor):
        super().__init__()
        self.graph = graph
        self.editor = editor
        self.graph_scene = GraphScene(self.graph)
        self.setScene(self.graph_scene)
        
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.dragging_edge = None
        self.drag_start_port = None
        self.node_items = {}
        self.edge_items = {}
        
        self.scale_factor = 1.0

    def contextMenuEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        items = self.scene().items(scene_pos)
        if not items:
            self.show_node_palette(scene_pos)
            event.accept()
        else:
            event.ignore()

    def show_node_palette(self, scene_pos):
        palette = NodePalette(self)
        palette.node_selected.connect(
            lambda node_type: self._add_node_from_palette(node_type, scene_pos)
        )

        view_pos = self.mapFromScene(scene_pos)
        global_pos = self.viewport().mapToGlobal(view_pos)

        palette.move(global_pos)
        palette.show()

    def _add_node_from_palette(self, node_type, scene_pos):
        editor = self.editor
        node = editor.node_factory.create_node(node_type)
        if not node:
            return

        node.x = scene_pos.x()
        node.y = scene_pos.y()

        editor.graph.add_node(node)
        node_item = self.add_node_item(node)

        scene = self.scene()
        if scene.pending_port:
            self._auto_connect(scene.pending_port, node_item)
            scene.pending_port = None
            scene.pending_scene_pos = None


    def _auto_connect(self, from_port_item, node_item):
        scene = self.scene()
        want_input = not from_port_item.is_input

        for port_item in node_item.port_items.values():
            if port_item.is_input == want_input:
                if scene._is_valid_connection(from_port_item, port_item):
                    scene.drag_edge = EdgeItem()
                    scene.drag_edge.source_port = (
                        from_port_item if not from_port_item.is_input else port_item
                    )
                    scene.drag_edge.target_port = (
                        port_item if not port_item.is_input else from_port_item
                    )
                    scene.drag_edge.update_positions()
                    scene.edges.append(scene.drag_edge)
                    scene.addItem(scene.drag_edge)
                    return


    
    def add_node_item(self, node):
        node_item = NodeItem(node)
        node_item.setPos(node.x, node.y)
        self.graph_scene.addItem(node_item)
        self.node_items[node.id] = node_item
        return node_item
    
    def add_edge_item(self, edge):
        edge_item = EdgeItem(edge)
        self.graph_scene.addItem(edge_item)
        self.edge_items[edge.id] = edge_item
        self.update_edge_item(edge_item)
        return edge_item
    
    def update_edge_item(self, edge_item):
        source_node_item = self.node_items.get(edge_item.edge.source.node.id)
        target_node_item = self.node_items.get(edge_item.edge.target.node.id)
        
        if source_node_item and target_node_item:
            source_pos = source_node_item.get_port_scene_pos(edge_item.edge.source.id)
            target_pos = target_node_item.get_port_scene_pos(edge_item.edge.target.id)
            edge_item.set_positions(source_pos, target_pos)
    
    def update_all_edges(self):
        for edge_item in self.edge_items.values():
            self.update_edge_item(edge_item)
    
    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.scale_factor *= zoom_factor
        else:
            zoom_factor = zoom_out_factor
            self.scale_factor *= zoom_factor
        
        if 0.2 <= self.scale_factor <= 3.0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale_factor /= zoom_factor

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake_event = event.clone()
            fake_event.button = Qt.LeftButton
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.graph_scene.selectedItems():
                if isinstance(item, NodeItem):
                    self.remove_node_item(item.node.id)
        super().keyPressEvent(event)

    def remove_node_item(self, node_id):
        if node_id not in self.node_items:
            return

        node_item = self.node_items[node_id]

        # supprimer edges visuels
        for edge in list(self.graph_scene.edges):
            if (edge.source_port in node_item.port_items.values() or
                edge.target_port in node_item.port_items.values()):
                self.graph_scene.removeItem(edge)
                self.graph_scene.edges.remove(edge)

        self.graph_scene.removeItem(node_item)
        del self.node_items[node_id]
