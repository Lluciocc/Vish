from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QPainterPath, QPen, QColor
from core.graph import Port
from core.port_types import PORT_STYLES, PortStyle, PortType

class PortItem(QGraphicsPathItem):
    def __init__(self, port: Port, parent=None, is_input=False):
        style = PORT_STYLES[port.port_type]

        super().__init__(self.generate_path(port, style), parent)

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

    def generate_path(self, port: Port, style: PortStyle) -> QPainterPath:
        retval = QPainterPath()
        match port.port_type:
            # Exec: triangular arrow
            case PortType.EXEC:
                half = style.size / 2
                retval.moveTo(-half, -half)
                retval.lineTo(0, -half)
                retval.lineTo(half, 0)
                retval.lineTo(0, half)
                retval.lineTo(-half, half)
                retval.closeSubpath()
            # Default path
            case _:
                half = style.size / 2
                retval.addEllipse(-half, -half, style.size, style.size)
                retval.closeSubpath()

        return retval

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
