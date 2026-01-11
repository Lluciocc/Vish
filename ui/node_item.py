from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from core.graph import Node
from .port_item import PortItem

class NodeItem(QGraphicsItem):
    WIDTH = 180
    HEADER_HEIGHT = 35
    PORT_SPACING = 25
    PORT_OFFSET = 15
    
    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.port_items = {}
        
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        self.title_item = QGraphicsTextItem(node.title, self)
        self.title_item.setDefaultTextColor(QColor("#ECF0F1"))
        self.title_item.setPos(10, 8)
        
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