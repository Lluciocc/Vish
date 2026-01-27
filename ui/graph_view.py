from PySide6.QtWidgets import QGraphicsView,QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QEvent
from PySide6.QtGui import QPainter, QColor, QCursor, QMouseEvent, QKeySequence
from core.graph import Port
from ui.palette import NodePalette
from ui.graph_scene import GraphScene
from ui.node_item import NodeItem
from ui.edge_item import EdgeItem
from ui.comment_box import CommentBoxItem
from theme.theme import Theme
from core.clipboard import GraphClipboard
from core.serializer import Serializer
from nodes.registry import create_node
from core.debug import Debug


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
        self.clipboard = GraphClipboard()
        self.serializer = Serializer(self.graph)
        self.node_factory = create_node
        self.paste_offset = (30, 30)

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
        source_node_item = self.node_items.get(edge.source.node.id)
        target_node_item = self.node_items.get(edge.target.node.id)
        if not source_node_item or not target_node_item:
            return None

        src_port_item = source_node_item.port_items.get(edge.source.id)
        tgt_port_item = target_node_item.port_items.get(edge.target.id)
        if not src_port_item or not tgt_port_item:
            return None

        edge_item = EdgeItem()
        edge_item.source_port = src_port_item
        edge_item.target_port = tgt_port_item
        edge_item.edge = edge

        self.graph_scene.addItem(edge_item)
        edge_item.update_positions()

        self.graph_scene.edges.append(edge_item)
        self.edge_items[edge.id] = edge_item
        return edge_item
    
    def remove_edge_item(self, edge_id):
        edge_item = self.edge_items.get(edge_id)
        if not edge_item:
            return
        if edge_item.scene() is self.graph_scene:
            self.graph_scene.removeItem(edge_item)
        if edge_item in self.graph_scene.edges:
            self.graph_scene.edges.remove(edge_item)
        del self.edge_items[edge_id]


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
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
            return

        if event.matches(QKeySequence.Paste):
            view_pos = self.mapFromGlobal(QCursor.pos())
            scene_pos = self.mapToScene(view_pos)
            self.paste(scene_pos)
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

        for edge_item in list(self.graph_scene.edges):
            if (
                edge_item.source_port in node_item.port_items.values()
                or edge_item.target_port in node_item.port_items.values()
            ):
                if edge_item.edge:
                    self.graph.remove_edge(edge_item.edge.id)
                    if edge_item.edge.id in self.edge_items:
                        del self.edge_items[edge_item.edge.id]

                if edge_item.scene() is self.graph_scene:
                    self.graph_scene.removeItem(edge_item)

                self.graph_scene.edges.remove(edge_item)

        self.graph.remove_node(node_id)

        if node_item.scene() is self.graph_scene:
            self.graph_scene.removeItem(node_item)

        del self.node_items[node_id]

    def get_selected_node_items(self):
        return [
            item for item in self.graph_scene.selectedItems()
            if hasattr(item, "node")
        ]

    def get_selected_nodes(self):
        return [item.node for item in self.get_selected_node_items()]
    
    # TODO: CTRL X / CTRL D/ CTRL A/ F to cut/duplicate/select all/focus node
    def copy_selection(self):
        nodes = self.get_selected_nodes()
        if not nodes:
            return

        self.paste_offset = (30, 30)
        Debug.Log(f"Copying {len(nodes)} nodes")

        data = self.serializer.serialize_subgraph(nodes)
        self.clipboard.set(data)

    def paste(self, scene_pos=None):
        if not self.clipboard.has_data():
            return

        data = self.clipboard.get()
        id_map = {}

        nodes_data = data.get("nodes", [])
        if not nodes_data:
            return

        avg_x = sum(n["x"] for n in nodes_data) / len(nodes_data)
        avg_y = sum(n["y"] for n in nodes_data) / len(nodes_data)

        if scene_pos:
            dx = scene_pos.x() - avg_x
            dy = scene_pos.y() - avg_y
        else:
            dx, dy = self.paste_offset

        for node_data in nodes_data:
            node = self.node_factory(node_data["type"])
            node.properties.update(node_data.get("properties", {}))
            node.x = node_data["x"] + dx
            node.y = node_data["y"] + dy

            self.graph.add_node(node)
            self.add_node_item(node)
            id_map[node_data["id"]] = node

        for edge_data in data.get("edges", []):
            src_node = id_map.get(edge_data["source_node"])
            tgt_node = id_map.get(edge_data["target_node"])
            if not src_node or not tgt_node:
                continue

            src_i = edge_data["source_output_index"]
            tgt_i = edge_data["target_input_index"]

            if src_i >= len(src_node.outputs) or tgt_i >= len(tgt_node.inputs):
                continue

            src_port = src_node.outputs[src_i]
            tgt_port = tgt_node.inputs[tgt_i]

            edge = self.graph.add_edge(src_port, tgt_port)
            if edge:
                self.add_edge_item(edge)

        self.paste_offset = (self.paste_offset[0] + 10, self.paste_offset[1] + 10)
        Debug.Log(f"Pasted {len(nodes_data)} nodes")

    def apply_theme(self):
        self.setBackgroundBrush(QColor(Theme.BACKGROUND))
        self.viewport().update()

