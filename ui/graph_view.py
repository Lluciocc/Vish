from PySide6.QtWidgets import QGraphicsView,QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QEvent
from PySide6.QtGui import QPainter, QColor, QCursor, QMouseEvent
from core.graph import Port
from ui.palette import NodePalette
from ui.graph_scene import GraphScene
from ui.node_item import NodeItem
from ui.edge_item import EdgeItem
from ui.comment_box import CommentBoxItem
from theme.theme import Theme


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
        self.setBackgroundBrush(QColor(Theme.BACKGROUND))

        self.node_items = {}
        self.edge_items = {}
        self.scale_factor = 1.0
        self._palette = None

    def contextMenuEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        items = self.scene().items(scene_pos)
        if items:
            super().contextMenuEvent(event)
            return
        
        self.show_node_palette(scene_pos)
        event.accept()

    def show_node_palette(self, scene_pos):
        if self._palette and self._palette.isVisible():
            self._palette.close()

        palette = NodePalette(self)
        self._palette = palette

        palette.node_selected.connect(
            lambda node_type: self._add_node_from_palette(node_type, scene_pos)
        )

        view_pos = self.mapFromScene(scene_pos)
        global_pos = self.viewport().mapToGlobal(view_pos)

        palette.move(global_pos)
        palette.show()

    def close_node_palette(self):
        if self._palette and self._palette.isVisible():
            self._palette.close()
        self._palette = None

    def _add_node_from_palette(self, node_type, scene_pos):
        editor = self.editor
        node = editor.node_factory.create_node(node_type)
        if not node:
            self.close_node_palette()
            return

        node.x = scene_pos.x()
        node.y = scene_pos.y()

        editor.graph.add_node(node)
        node_item = self.add_node_item(node)

        scene = self.scene()
        if scene.pending_port and scene.drag_edge:
            from_port_item = scene.pending_port
            scene.pending_port = None
            scene.pending_scene_pos = None

            target_port_item = None
            want_input = not from_port_item.is_input

            for p in node_item.port_items.values():
                if p.is_input == want_input:
                    target_port_item = p
                    break

            if target_port_item:
                scene.finalize_connection(from_port_item, target_port_item)
            else:
                scene._cancel_drag_edge()

        self.close_node_palette()

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
            fake = QMouseEvent(
                QEvent.MouseButtonPress,
                event.position(),
                Qt.LeftButton,
                Qt.LeftButton,
                event.modifiers()
            )
            super().mousePressEvent(fake)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        focus_item = self.scene().focusItem()
        if isinstance(focus_item, QGraphicsTextItem):
            super().keyPressEvent(event)
            return
        if event.key() == Qt.Key_C:
            self.create_comment_box()
            event.accept()
            return

        if event.key() == Qt.Key_Delete:
            for item in self.graph_scene.selectedItems():
                if isinstance(item, NodeItem):
                    self.remove_node_item(item.node.id)
                elif isinstance(item, CommentBoxItem):
                    self.graph_scene.removeItem(item)
            event.accept()
            return

        super().keyPressEvent(event)

    def create_comment_box(self):
        view_pos = self.mapFromGlobal(QCursor.pos())
        scene_pos = self.mapToScene(view_pos)

        box = CommentBoxItem(title="Comment")
        box.setPos(scene_pos)
        self.scene().addItem(box)


    def remove_node_item(self, node_id):
        if node_id not in self.node_items:
            return

        node_item = self.node_items[node_id]
        self.graph.remove_node(node_id)

        for edge in list(self.graph_scene.edges):
            if (edge.source_port in node_item.port_items.values() or
                edge.target_port in node_item.port_items.values()):
                if edge.edge:
                    self.graph.remove_edge(edge.edge.id)
                if edge.scene() is self.graph_scene:
                    self.graph_scene.removeItem(edge)
                self.graph_scene.edges.remove(edge)

        self.graph_scene.removeItem(node_item)
        del self.node_items[node_id]
    
    def apply_theme(self):
        self.setBackgroundBrush(QColor(Theme.BACKGROUND))
        self.viewport().update()

