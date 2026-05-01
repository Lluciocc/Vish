from commands.undo_commands import *
from core.config import Config
from core.clipboard import GraphClipboard
from core.debug import Debug, Info
from core.graph import Port
from core.icons import Icon
from core.layout import GraphLayoutEngine
from core.port_types import PortType
from core.serializer import Serializer
from nodes.registry import create_node
from PySide6.QtCore import Property, QEasingCurve, QEvent, QPointF, QPropertyAnimation, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QKeySequence, QMouseEvent, QPainter, QUndoStack
from PySide6.QtWidgets import QApplication, QGraphicsRectItem, QGraphicsTextItem, QGraphicsView, QHBoxLayout, QLabel, QPushButton, QSlider, QWidget
from theme.theme import Theme
from ui.comment_box import CommentBoxItem
from ui.edge_item import EdgeItem
from ui.graph_scene import GraphScene
from ui.node_item import NodeItem
from ui.palette import NodePalette


class ZoomLabel(QLabel):
    def mouseDoubleClickEvent(self, event):
        self.parent().parent().set_zoom(1.0, animated=True)


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
    clear_property_panel_request = Signal()

    def __init__(self, graph, editor):
        super().__init__()
        self.graph = graph
        self.editor = editor
        self.graph_scene = GraphScene(self.graph)
        self.setScene(self.graph_scene)
        self.graph_scene.setSceneRect(-50000, -50000, 100000, 100000)

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(Theme.BACKGROUND))

        self.alt_lang = False
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
        self._init_frame_button()
        self._suspend_edge_undo = False
        self.undo_stack = QUndoStack(self)
        self.graph_scene.connection_created.connect(
            lambda a, b: (
                None if self._suspend_edge_undo
                else self.undo_stack.push(AddEdgeCommand(self, a, b))
            )
        )

    def get_zoom(self):
        return self.scale_factor

    def _set_zoom_anim_value(self, value):
        self._apply_zoom(value)

    zoom_anim_value = Property(
        float,
        get_zoom,
        _set_zoom_anim_value
    )

    def contextMenuEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        items = self.scene().items(scene_pos)
        if items:
            super().contextMenuEvent(event)
            return

        self.setDragMode(QGraphicsView.NoDrag)
        self.show_node_palette(scene_pos)
        event.accept()

    def show_node_palette(self, scene_pos):
        if self.graph_scene.block_input:
            return

        if self._palette and self._palette.isVisible():
            self._palette.close()

        palette = NodePalette(self)
        self._palette = palette

        palette.node_selected.connect(
            lambda node_type: self._add_node_from_palette(node_type, scene_pos)
        )

        view_pos = self.mapFromScene(scene_pos)
        global_pos = self.viewport().mapToGlobal(view_pos)
        self.gpos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))

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
        node_item = self.node_items.get(node.id)

        scene = self.scene()
        if scene.drag_edges:
            source_port = scene.drag_edges[0].source_port
            valid_port = None

            target_port = None
            target_is_input = not source_port.is_input

            for port in node_item.port_items.values():
                if port.is_input == target_is_input:
                    target_port = port
                    valid = scene._is_valid_connection(source_port, target_port)
                    if valid:
                        valid_port = target_port
                        break

            if valid_port:
                for edge in scene.drag_edges:
                    if target_is_input:
                        scene.set_edge(edge.source_port, valid_port, edge)
                    else:
                        scene.set_edge(valid_port, edge.source_port, edge)
                scene.drag_edges.clear()
            else:
                scene._cancel_drag_edge()

        self.close_node_palette()

    def add_node_item(self, node):
        node_item = NodeItem(node)
        node_item.setPos(node.x, node.y)
        node_item.setZValue(node.z)
        self.graph_scene.addItem(node_item)
        self.node_items[node.id] = node_item
        return node_item

    def wheelEvent(self, event):
        zoom_step = 1.15
        min_scale = 0.2
        max_scale = 3.0

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        current_scale = self.transform().m11()
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_step
        else:
            zoom_factor = 1 / zoom_step

        proposed_scale = current_scale * zoom_factor

        if min_scale <= current_scale <= max_scale:
            proposed_scale = max(min_scale, min(max_scale, proposed_scale))
        else:
            if current_scale > max_scale and proposed_scale > current_scale:
                return
            if current_scale < min_scale and proposed_scale < current_scale:
                return

        applied_factor = proposed_scale / current_scale
        self.scale(applied_factor, applied_factor)

        self._sync_zoom_from_transform()

    def viewportEvent(self, event):
        if isinstance(event, QMouseEvent):
            if event.button() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier: # Ctrl + MB
                current_scale = self.transform().m11()
                applied_factor = 1 / current_scale
                self.scale(applied_factor, applied_factor)
                self._sync_zoom_from_transform()
                return True

            elif event.type() == QEvent.MouseButtonPress and event.button() == Qt.MiddleButton: # MB begin
                self._previous_drag_mode = self.dragMode()
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                self.setInteractive(False)

                fake = QMouseEvent(
                    QEvent.MouseButtonPress,
                    event.position(),
                    Qt.LeftButton,
                    Qt.LeftButton,
                    event.modifiers()
                )
                super().mousePressEvent(fake)
                return True

            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.MiddleButton: # MB end
                self.setInteractive(True)
                fake = QMouseEvent(
                    QEvent.MouseButtonRelease,
                    event.position(),
                    Qt.LeftButton,
                    Qt.NoButton,
                    event.modifiers()
                )
                super().mouseReleaseEvent(fake)

                self.setDragMode(self._previous_drag_mode)
                return True

        return super().viewportEvent(event)

    def keyPressEvent(self, event):
        focus_item = self.scene().focusItem()
        if isinstance(focus_item, QGraphicsTextItem):
            super().keyPressEvent(event)
            return
        if event.matches(QKeySequence.Copy): # Ctrl+C
            self.copy_selection()
            return
        if event.key() == Qt.Key_Space and event.modifiers() & Qt.ControlModifier: # Ctrl+Space
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
            self.clear_property_panel_request.emit()
            if Config.SYNC_NODES_AND_GEN:
                self.graph_scene.graph_changed.emit()
            return

        if event.matches(QKeySequence.Redo) or (event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier): # Ctrl+Shift+Z or Ctrl+Y
            self.undo_stack.redo()
            self.clear_property_panel_request.emit()

            return
        if event.matches(QKeySequence.SelectAll): # Ctrl+A
            self.scene().clearSelection()
            for item in self.scene().items():
                if isinstance(item, NodeItem):
                    item.setSelected(True)
            if Config.SYNC_NODES_AND_GEN:
                self.graph_scene.graph_changed.emit()
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
        if event.matches(QKeySequence.Delete): # Del
            self.clear_property_panel_request.emit()
            selected_items = self.scene().selectedItems()

            node_items = [it for it in selected_items if isinstance(it, NodeItem)]
            comment_items = [it for it in selected_items if isinstance(it, CommentBoxItem)]

            if node_items or comment_items:
                self.undo_stack.beginMacro("Delete") # both macro in the same key seq

                for it in node_items:
                    self.undo_stack.push(RemoveNodeCommand(self, it.node.id))

                for it in comment_items:
                    self.undo_stack.push(RemoveCommentCommand(self, it))

                self.undo_stack.endMacro()

                if Config.SYNC_NODES_AND_GEN:
                    self.graph_scene.graph_changed.emit()

                event.accept()
                return

        if event.key() == Qt.Key_F: # F
            self.auto_layout()
            return
        if event.key() == Qt.Key_R: # R
            self.rebuild_graph()
            return
        if event.key() == Qt.Key_H: # H
            self.frame_all()
            return

        if event.key() == Qt.Key_Alt and Config.lang != "en": # Alt
            self.alt_lang = True
            for item in self.scene().items():
                if isinstance(item, NodeItem):
                    NodeItem.update_traduction(item, "en")

        if event.modifiers() == Qt.KeypadModifier:
            current_scale = self.transform().m11()
            divisor = 4
            if event.key() == Qt.Key_Plus: # Num+
                zoom_factor = 1 / (1 - 1 / divisor)
                proposed_scale = current_scale * zoom_factor
                self.set_zoom(proposed_scale, animated=True)
                return
            elif event.key() == Qt.Key_Minus: # Num-
                zoom_factor = 1 / (1 + 1 / (divisor - 1))
                proposed_scale = current_scale * zoom_factor
                self.set_zoom(proposed_scale, animated=True)
                return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.revert_language()
        super().keyReleaseEvent(event)

    def focusOutEvent(self, event):
        self.revert_language()
        super().focusOutEvent(event)

    def revert_language(self):
        if self.alt_lang:
            self.alt_lang = False
            for item in self.scene().items():
                if isinstance(item, NodeItem):
                    NodeItem.update_traduction(item, Config.lang)

    def mousePressEvent(self, event):
        if self._palette and self._palette.isVisible():
            self.close_node_palette()
            event.accept()
            return
        item = self.itemAt(event.pos())
        if isinstance(item, NodeItem): # can't drag if click on node
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event): # restore drag mode after dragging
        if event.button() == Qt.LeftButton:
            self.graph_scene.block_input = False

        self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def create_comment_box(self):
        view_pos = self.mapFromGlobal(QCursor.pos())
        scene_pos = self.mapToScene(view_pos)

        box = CommentBoxItem(title="Comment")
        box.setPos(scene_pos)
        self.undo_stack.push(AddCommentCommand(self, box))

    def frame_all(self):
        rect = self.scene().itemsBoundingRect()
        if rect.isNull():
            return
        rect = rect.adjusted(-200, -200, 200, 200)
        self.fitInView(rect, Qt.KeepAspectRatio)
        self._sync_zoom_from_transform()

    def remove_node_item(self, node_id):
        if node_id not in self.node_items:
            return

        node_item = self.node_items[node_id]

        for port in node_item.port_items.values():
            for edge in port.edges:
                self.graph_scene.drag_edges.append(edge)
            self.graph_scene.delete_edges()

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
            source_node = id_map.get(edge_data["source_node"])
            target_node = id_map.get(edge_data["target_node"])
            if not source_node or not target_node:
                continue

            source_i = edge_data["source_output_index"]
            target_i = edge_data["target_input_index"]

            if source_i >= len(source_node.outputs) or target_i >= len(target_node.inputs):
                continue

            source_port = source_node.outputs[source_i]
            target_port = target_node.inputs[target_i]

            edge = self.graph.add_edge(source_port, target_port)
            if edge:
                self.graph_scene.add_core_edge(edge, self.node_items)

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
        self.frame_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BUTTON};
                border: 1px solid #555;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
        """)
        self.zoom_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {Theme.ACCENT};
                border-radius: 3px;
            }}

            QSlider::sub-page:horizontal {{
                background: {Theme.ACCENT};
                border-radius: 3px;
            }}

            QSlider::add-page:horizontal {{
                background: {Theme.PANEL};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: {Theme.ACCENT};
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)
        self.frame_btn.setIcon(self.get_icon("frame"))
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
        if hasattr(self, "frame_btn"):
            self._update_frame_button_position()
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
        old_transform_anchor = self.transformationAnchor()
        old_resize_anchor = self.resizeAnchor()

        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

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

        self.setTransformationAnchor(old_transform_anchor)
        self.setResizeAnchor(old_resize_anchor)

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
        self.zoom_label.setFixedWidth(32)
        self.zoom_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.zoom_slider = QSlider(Qt.Horizontal)

        self.zoom_slider.setRange(20, 300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {Theme.ACCENT};
                border-radius: 3px;
            }}

            QSlider::sub-page:horizontal {{
                background: {Theme.ACCENT};
                border-radius: 3px;
            }}

            QSlider::add-page:horizontal {{
                background: {Theme.PANEL};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: {Theme.ACCENT};
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)

        self.zoom_out_btn.clicked.connect(lambda: self._step_zoom(-1))
        self.zoom_in_btn.clicked.connect(lambda: self._step_zoom(1))
        self.zoom_slider.valueChanged.connect(self._on_zoom_slider_changed)

        layout.addWidget(self.zoom_out_btn)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.zoom_in_btn)
        layout.addWidget(self.zoom_slider)

        self.zoom_widget.move(10, self.height() - 42)
        self.zoom_widget.show()

    def _sync_zoom_from_transform(self):
        actual_scale = self.transform().m11() # assuming uniform scaling, m11() is enough: https://doc.qt.io/qtforpython-6.5/PySide6/QtGui/QTransform.html

        self.scale_factor = actual_scale

        percent = int(actual_scale * 100)
        self.zoom_label.setText(f"{percent}%")

        slider_value = max(self.zoom_slider.minimum(), min(self.zoom_slider.maximum(), percent))
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(slider_value)
        self.zoom_slider.blockSignals(False)

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

        if source_output and target_input:                                      #TODO outdated code
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

    def update_language(self):
        for item in self.scene().items():
            if isinstance(item, NodeItem):
                NodeItem.update_traduction(item, Config.lang)

    def _init_frame_button(self):
        self.frame_btn = QPushButton(self)
        self.frame_btn.setFixedSize(36, 36)
        self.frame_btn.setCursor(Qt.PointingHandCursor)
        self.frame_btn.setIcon(self.get_icon("frame"))
        self.frame_btn.setIconSize(self.frame_btn.size() * 0.8125)

        self.frame_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BUTTON};
                border: 1px solid #555;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
        """)

        self.frame_btn.clicked.connect(self.frame_all)

        self._update_frame_button_position()
        self.frame_btn.show()

    def _update_frame_button_position(self):
        margin = 10
        x = self.width() - self.frame_btn.width() - margin
        y = self.height() - self.frame_btn.height() - margin
        self.frame_btn.move(x, y)

    def get_icon(self, name):
        icon = Icon.load_icon("main", name)
        return icon
