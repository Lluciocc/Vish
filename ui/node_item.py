from unicodedata import category
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from core.graph import Node
from theme.theme import Theme
from ui.port_item import PortItem
from nodes.registry import NODE_REGISTRY
from core.traduction import Traduction
from core.icons import Icon
import os

class NodeItem(QGraphicsItem):
    WIDTH = 180
    HEADER_HEIGHT = 35
    PORT_SPACING = 25
    PORT_OFFSET = 15
    
    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.port_items = {}
        self.icon_item = None

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        self.title_item = QGraphicsTextItem(Traduction.get_trad(node.node_type, node.title), self)
        self.title_item.setDefaultTextColor(QColor("#ECF0F1"))
        self.title_item.setPos(10, 8)
        self.setZValue(1)
        
        self.setup_icon()
        self.setup_ports()
        
        self.height = self.HEADER_HEIGHT + max(
            len(node.inputs) * self.PORT_SPACING,
            len(node.outputs) * self.PORT_SPACING
        ) + 20
    
    def setup_ports(self):
        for i, port in enumerate(self.node.inputs):
            port_item = PortItem(port, self, is_input=True)
            y_pos = self.HEADER_HEIGHT + self.PORT_OFFSET + i * self.PORT_SPACING
            port_item.setPos(0, y_pos)
            self.port_items[port.id] = port_item
        
        for i, port in enumerate(self.node.outputs):
            port_item = PortItem(port, self, is_input=False)
            y_pos = self.HEADER_HEIGHT + self.PORT_OFFSET + i * self.PORT_SPACING
            port_item.setPos(self.WIDTH, y_pos)
            self.port_items[port.id] = port_item
    
    def boundingRect(self):
        return QRectF(0, 0, self.WIDTH, self.height)
    
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 8, 8)

        if self.isSelected():
            painter.setPen(QPen(QColor("#3498DB"), 3))
        else:
            painter.setPen(QPen(QColor("#2C3E50"), 2))

        painter.setBrush(QBrush(QColor("#34495E")))
        painter.drawPath(path)

        header_rect = QRectF(0, 0, self.WIDTH, self.HEADER_HEIGHT)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 8, 8)

        painter.setBrush(QBrush(QColor(self.node.color)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(header_path)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            scene = self.scene()
            if scene:
                scene.update_edges_for_node(self)
            self.node.x = value.x()
            self.node.y = value.y()

        elif change == QGraphicsItem.ItemSelectedChange and value:
            scene = self.scene()
            if scene and hasattr(scene, "_z_counter"):
                self.setZValue(scene._z_counter)
                scene._z_counter += 1

        return super().itemChange(change, value)
 
    def get_port_scene_pos(self, port_id: str) -> QPointF:
        if port_id in self.port_items:
            port_item = self.port_items[port_id]
            return self.mapToScene(port_item.pos())
        return QPointF()

    def mousePressEvent(self, event):
        scene = self.scene()
        if scene:
            scene.node_selected.emit(self.node)

            if hasattr(scene, "_z_counter"):
                self.setZValue(scene._z_counter)
                scene._z_counter += 1

        super().mousePressEvent(event)

    def rebuild_ports(self):
        scene = self.scene()

        old_ports = self.port_items.copy()

        for port_item in old_ports.values():
            if port_item.scene():
                port_item.scene().removeItem(port_item)

        self.port_items.clear()

        self.prepareGeometryChange()

        self.setup_ports()

        self.height = self.HEADER_HEIGHT + max(
            len(self.node.inputs) * self.PORT_SPACING,
            len(self.node.outputs) * self.PORT_SPACING
        ) + 20

        if scene:
            for edge_item in list(scene.edges):
                edge = edge_item.edge

                if edge.source.node.id == self.node.id:
                    new_port = self.port_items.get(edge.source.id)
                    if new_port:
                        edge_item.source_port = new_port
                    else:
                        scene.graph.remove_edge(edge.id)
                        if edge_item.scene():
                            scene.removeItem(edge_item)
                        scene.edges.remove(edge_item)
                        continue

                if edge.target.node.id == self.node.id:
                    new_port = self.port_items.get(edge.target.id)
                    if new_port:
                        edge_item.target_port = new_port
                    else:
                        scene.graph.remove_edge(edge.id)
                        if edge_item.scene():
                            scene.removeItem(edge_item)
                        scene.edges.remove(edge_item)
                        continue

                edge_item.update_positions()

            scene.update_edges_for_node(self)

        self.update()
        
    def get_icon_node(self, item: Node, icon_size, padding):
        node = NODE_REGISTRY.get(item.title.lower().replace(" ", "_"))
        if node is not None:
            icon = Icon.load_item(self, "nodes/"+node["category"], item.title, icon_size, padding)

    def setup_icon(self):
        icon_size = 24
        padding = 6
        self.get_icon_node(self.node, icon_size, padding)

        text_x = icon_size + padding
        text_rect = self.title_item.boundingRect()
        text_y = (self.HEADER_HEIGHT - text_rect.height()) / 2
        self.title_item.setPos(text_x, text_y)
