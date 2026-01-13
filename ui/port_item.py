from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QPen, QColor
from core.graph import Port
from core.port_types import PORT_STYLES

class PortItem(QGraphicsEllipseItem):
    def __init__(self, port: Port, parent=None, is_input=False):
        style = PORT_STYLES[port.port_type]
        size = style.size

        super().__init__(-size / 2, -size / 2, size, size, parent)

        self.port = port
        self.is_input = is_input

        self.setBrush(QBrush(QColor(style.color)))
        self.setPen(QPen(QColor("#2C3E50"), 2))

        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setZValue(10)
        # SET THE TOOLTIP
        self.setToolTip(self.port.tooltip)

        self.highlight = False

    def center_scene_pos(self):
        return self.mapToScene(self.boundingRect().center())

    def mousePressEvent(self, event):
        print("PORT CLICK")

    
    def hoverEnterEvent(self, event):
        self.highlight = True
        self.setPen(QPen(QColor("#ECF0F1"), 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.highlight = False
        self.setPen(QPen(QColor("#2C3E50"), 2))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.scene().start_connection(self)

    def mouseReleaseEvent(self, event):
        scene = self.scene()
        if scene:
            scene.end_connection(self)
        event.accept()
