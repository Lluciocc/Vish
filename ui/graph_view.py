from PySide6.QtWidgets import QGraphicsView,QGraphicsRectItem, QGraphicsTextItem, QWidget, QHBoxLayout, QSlider, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QEvent, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QCursor, QMouseEvent, QKeySequence, QUndoStack
from core.graph import Port
from core.port_types import PortType
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
from commands.undo_commands import *
from core.layout import GraphLayoutEngine

class ZoomLabel(QLabel):
    def mouseDoubleClickEvent(self, event):
        self.parent().set_zoom(1.0, animated=True)

# class MiniMap(QGraphicsView):
#     def __init__(self, scene, parent):
#         super().__init__(scene, parent)
#         self.setRenderHint(QPainter.Antialiasing)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setInteractive(False)
#         self.setStyleSheet("background: rgba(20,20,20,180); border: 1px solid #444;")
#         self.scale(0.1, 0.1)

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
        self._init_zoom_widget()
        self._zoom_anim = QPropertyAnimation(self, b"zoom_anim_value")
        self._zoom_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._zoom_anim.setDuration(120)
    #     self._init_minimap()
        self._suspend_edge_undo = False
        self.undo_stack = QUndoStack(self)
        self.graph_scene.connection_created.connect(
            lambda a, b: (
                None if self._suspend_edge_undo
                else self.undo_stack.push(AddEdgeCommand(self, a, b))
            )
        )

    def _get_zoom_anim_value(self):
        return self.scale_factor

    def _set_zoom_anim_value(self, value):
        self._apply_zoom(value)

    zoom_anim_value = Property(
        float,
        _get_zoom_anim_value,
        _set_zoom_anim_value
    )

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

        self.undo_stack.push(AddNodeCommand(self, node))
        self.undo_stack.undo()
        self.undo_stack.redo()
        node_item = self.node_items.get(node.id)


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
        zoom_step = 1.15
        if event.angleDelta().y() > 0:
            new_factor = self.scale_factor * zoom_step
        else:
            new_factor = self.scale_factor / zoom_step
        self.set_zoom(new_factor, animated=True)


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
        if event.button() == Qt.MouseButton.MiddleButton:
            fake_event = QMouseEvent(
                event.type(),
                event.localPos(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
                event.modifiers()
            )
            super().mouseReleaseEvent(fake_event)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        focus_item = self.scene().focusItem()
        if isinstance(focus_item, QGraphicsTextItem):
            super().keyPressEvent(event)
            return
        if event.matches(QKeySequence.Copy): # Ctrl+C
            self.copy_selection()
            return
        if event.key() == Qt.Key_Space and event.modifiers() & Qt.ControlModifier:
            selected = self.get_selected_node_items()
            if len(selected) == 1:
                self._open_palette_from_selected(selected[0])
                event.accept()
                return
        if event.matches(QKeySequence.Paste): # Ctrl+V
            if self.clipboard.has_data():
                view_pos = self.mapFromGlobal(QCursor.pos())
                scene_pos = self.mapToScene(view_pos)
                self.undo_stack.push(PasteCommand(self, self.clipboard.get(), scene_pos))
            return
        if event.key() == Qt.Key_C: # C 
            self.create_comment_box()
            event.accept()
            return
        if event.matches(QKeySequence.Undo): # Ctrl+Z
            self.undo_stack.undo()
            return

        if event.matches(QKeySequence.Redo) or (event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier): # Ctrl+Shift+Z or Ctrl+Y
            self.undo_stack.redo()
            return
        if event.matches(QKeySequence.SelectAll): # Ctrl+A
            self.scene().clearSelection()
            for item in self.scene().items():
                if isinstance(item, NodeItem):
                    item.setSelected(True)
            return
        if event.matches(QKeySequence.Cut): # Ctrl+X
            self.copy_selection()
            selected_node_items = self.get_selected_node_items()
            if selected_node_items:
                self.undo_stack.beginMacro("Cut")
                for item in selected_node_items:
                    self.undo_stack.push(RemoveNodeCommand(self, item.node.id))
                self.undo_stack.endMacro()
            return
        if event.key() == Qt.Key_D and event.modifiers() & Qt.ControlModifier: # Ctrl+D
            self.copy_selection()
            self.paste()
            return
        if event.matches(QKeySequence.Delete): # Ctrl+Delete
            node_items = [it for it in self.graph_scene.selectedItems() if isinstance(it, NodeItem)]
            if node_items:
                self.undo_stack.beginMacro("Delete")
                for it in node_items:
                    self.undo_stack.push(RemoveNodeCommand(self, it.node.id))
                self.undo_stack.endMacro()
            event.accept()
            return
        if event.key() == Qt.Key_F: # F
            self.auto_layout()
            return
        if event.key() == Qt.Key_R: # R
            self.rebuild_graph()
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
                    if edge_item.edge and edge_item.edge.id in self.graph.edges:
                        self.graph.remove_edge(edge_item.edge.id)
                    if edge_item.edge.id in self.edge_items:
                        del self.edge_items[edge_item.edge.id]
                        self.graph.remove_edge(edge_item.edge.id)
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
    
    def copy_selection(self, message=True):
        nodes = self.get_selected_nodes()
        if not nodes:
            return

        self.paste_offset = (30, 30)
        if message:
            Debug.Log(f"Copying {len(nodes)} nodes")

        data = self.serializer.serialize_subgraph(nodes)
        self.clipboard.set(data)

    def paste(self, scene_pos=None, message=True):
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
        if message:
            Debug.Log(f"Pasted {len(nodes_data)} nodes")

    def auto_layout(self):
        l = GraphLayoutEngine(self.graph)
        positions = l.compute()

        for node_id, (x, y) in positions.items():
            node = self.graph.nodes.get(node_id)
            if not node:
                continue
            node.x = x
            node.y = y
            item = self.node_items.get(node_id)
            if item:
                item.setPos(x, y)
                self.graph_scene.update_edges_for_node(item)


    def apply_theme(self):
        self.setBackgroundBrush(QColor(Theme.BACKGROUND))
        self.viewport().update()

    # def centerOn(self, *args):
    #     super().centerOn(*args)
    #     if hasattr(self, "minimap"):
    #         self.minimap.centerOn(*args)

    # def _init_minimap(self):
    #     self.minimap = MiniMap(self.graph_scene, self)
    #     self.minimap.setFixedSize(180, 140)
    #     self.minimap.move(self.width() - 190, self.height() - 150)
    #     self.minimap.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "zoom_widget"):
            self.zoom_widget.move(10, self.height() - 42)
        # if hasattr(self, "minimap"):
        #     self.minimap.move(self.width() - 190, self.height() - 150)

    def set_zoom(self, factor, animated=False):
        factor = max(0.2, min(3.0, factor))

        if animated:
            self._zoom_anim.stop()
            self._zoom_anim.setStartValue(self.scale_factor)
            self._zoom_anim.setEndValue(factor)
            self._zoom_anim.start()
        else:
            self._apply_zoom(factor)

    def _apply_zoom(self, factor):
        self.resetTransform()
        self.scale(factor, factor)

        self.scale_factor = factor

        percent = int(factor * 100)
        self.zoom_label.setText(f"{percent}%")

        slider_value = int(factor * 100)
        if self.zoom_slider.value() != slider_value:
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(slider_value)
            self.zoom_slider.blockSignals(False)

    def _on_zoom_slider_changed(self, value):
        self.set_zoom(value / 100.0)

    def _step_zoom(self, direction):
        step = 0.1
        self.set_zoom(self.scale_factor + direction * step, animated=True)

    def _init_zoom_widget(self):
        self.zoom_widget = QWidget(self)
        self.zoom_widget.setFixedHeight(32)

        layout = QHBoxLayout(self.zoom_widget)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(6)

        self.zoom_out_btn = QPushButton("-")
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn.setFixedSize(28, 28)
        self.zoom_in_btn.setFixedSize(28, 28)

        self.zoom_label = ZoomLabel("100%")
        self.zoom_slider = QSlider(Qt.Horizontal)

        self.zoom_slider.setRange(20, 300)
        self.zoom_slider.setValue(100)

        self.zoom_out_btn.clicked.connect(lambda: self._step_zoom(-1))
        self.zoom_in_btn.clicked.connect(lambda: self._step_zoom(1))
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider_changed)

        layout.addWidget(self.zoom_out_btn)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.zoom_in_btn)
        layout.addWidget(self.zoom_slider)

        self.zoom_widget.move(10, self.height() - 42)
        self.zoom_widget.show()

    def _open_palette_from_selected(self, node_item):
        scene_pos = node_item.sceneBoundingRect().center()

        if self._palette and self._palette.isVisible():
            self._palette.close()

        palette = NodePalette(self)
        self._palette = palette

        palette.node_selected.connect(
            lambda node_type: self._add_node_connected_to(node_type, node_item)
        )

        view_pos = self.mapFromScene(scene_pos)
        global_pos = self.viewport().mapToGlobal(view_pos)

        palette.move(global_pos)
        palette.show()

    def _add_node_connected_to(self, node_type, source_node_item):
        editor = self.editor
        node = editor.node_factory.create_node(node_type)
        if not node:
            self.close_node_palette()
            return

        source_rect = source_node_item.sceneBoundingRect()
        node.x = source_rect.right() + 120
        node.y = source_rect.center().y()

        self.undo_stack.push(AddNodeCommand(self, node))
        self.undo_stack.undo()
        self.undo_stack.redo()

        new_node_item = self.node_items.get(node.id)
        if not new_node_item:
            self.close_node_palette()
            return

        source_output = None
        target_input = None

        for p in source_node_item.port_items.values():
            if not p.is_input:
                source_output = p
                break

        for p in new_node_item.port_items.values():
            if p.is_input:
                target_input = p
                break

        if source_output and target_input:
            self.graph_scene.start_connection(source_output)
            self.graph_scene.finalize_connection(source_output, target_input)

        self.close_node_palette()

    def rebuild_graph(self):
        for item in self.scene().items():
            if isinstance(item, NodeItem):
                item.setSelected(True)
        self.copy_selection(message=False)
        node_items = [it for it in self.graph_scene.selectedItems() if isinstance(it, NodeItem)]
        for it in node_items:
            self.undo_stack.push(RemoveNodeCommand(self, it.node.id))
        self.paste_offset = (0, 0)
        self.paste(message=False)
        self.paste_offset = (30, 30)
        