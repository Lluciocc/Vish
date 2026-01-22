from unicodedata import category
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QIcon, QPixmap
from core.graph import Node
from theme.theme import Theme
from ui.port_item import PortItem
from nodes.registry import NODE_REGISTRY
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
        
        self.title_item = QGraphicsTextItem(node.title, self)
        self.title_item.setDefaultTextColor(QColor("#ECF0F1"))
        self.title_item.setPos(10, 8)
        
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
        super().mousePressEvent(event)

    def get_icon_node(self, item: Node):
        node = NODE_REGISTRY.get(item.title.lower())
        if node is not None:
            category = node["category"]
            path = "assets/icons/nodes/{}/{}.png".format(
                    category.lower().replace(" ", "_"),
                    item.title.lower().replace(" ", "_")
                )
            if os.path.exists(path):
                return QIcon(path)
            else:
                return QIcon("assets/icons/nodes/{}/default.png".format(category))
            
    def setup_icon(self):
        icon = self.get_icon_node(self.node)
        padding = 8
        spacing = 6
        icon_size = 18
        x = padding

        if icon and not icon.isNull():
            pixmap = icon.pixmap(
                icon_size,
                icon_size,
                QIcon.Normal,
                QIcon.On
            )
            self.icon_item = QGraphicsPixmapItem(pixmap, self)
            self.icon_item.setTransformationMode(Qt.SmoothTransformation)
            icon_y = (self.HEADER_HEIGHT - icon_size) / 2
            self.icon_item.setPos(x, icon_y)
            x += icon_size + spacing

        text_rect = self.title_item.boundingRect()
        text_y = (self.HEADER_HEIGHT - text_rect.height()) / 2
        self.title_item.setPos(x, text_y)

    # def setup_icon(self):
    #     svg_path = self.get_icon_node(self.node)
    #     padding = 8
    #     spacing = 6
    #     icon_size = 18
    #     x = padding

    #     if svg_path:
    #         self.icon_item = QGraphicsSvgItem(svg_path, self)
    #         bounds = self.icon_item.boundingRect()
    #         scale = icon_size / max(bounds.width(), bounds.height())
    #         self.icon_item.setScale(scale)
    #         icon_y = (self.HEADER_HEIGHT - bounds.height() * scale) / 2
    #         self.icon_item.setPos(x, icon_y)
    #         x += icon_size + spacing
    #     text_rect = self.title_item.boundingRect()
    #     text_y = (self.HEADER_HEIGHT - text_rect.height()) / 2
    #     self.title_item.setPos(x, text_y)
