from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainterPath, QPen, QColor
from core.graph import Edge
from core.port_types import PORT_STYLES, PortType

class EdgeItem(QGraphicsPathItem):
    def __init__(self, edge=None, source_port=None, target_port=None):
        super().__init__()
        self.edge = edge
        self.source_port = source_port
        self.target_port = target_port

        self.source_pos = QPointF()
        self.target_pos = QPointF()

        self.apply_style_from_source()
        self.setZValue(-1)

    def apply_style_from_source(self):
        if not self.source_port:
            color = QColor("#95A5A6")
            width = 3
        else:
            port_type = self.source_port.port.port_type
            style = PORT_STYLES.get(port_type)

            if style:
                color = QColor(style.color)
                width = style.thickness
            else:
                color = QColor("#95A5A6")
                width = 3
            if port_type == PortType.EXEC:
                color = QColor("#95A5A6")

        pen = QPen(color, width)
        pen.setCapStyle(Qt.RoundCap)
        self.setPen(pen)

    def update_positions(self):
        if self.source_port:
            self.source_pos = self.source_port.center_scene_pos()
        if self.target_port:
            self.target_pos = self.target_port.center_scene_pos()
        self.update_path()

    
    def set_positions(self, source: QPointF, target: QPointF):
        self.source_pos = source
        self.target_pos = target
        self.update_path()

    def set_target_pos(self, pos: QPointF, is_port_input):
        if is_port_input:
            self.source_pos = pos
        else:
            self.target_pos = pos
        self.update_path()

    
    def update_path(self):
        path = QPainterPath()
        path.moveTo(self.source_pos)
        
        dx = self.target_pos.x() - self.source_pos.x()
        dy = self.target_pos.y() - self.source_pos.y()

        ctrl1_x = self.source_pos.x() + min(max(abs(dy) * 2.5, abs(dx)), max(dx, pow(abs(dx), 0.8) + 250)) * 0.5
        ctrl1_y = self.source_pos.y()
        ctrl2_x = self.target_pos.x() - min(max(abs(dy) * 2.5, abs(dx)), max(dx, pow(abs(dx), 0.8) + 250)) * 0.5
        ctrl2_y = self.target_pos.y()
        
        path.cubicTo(
            QPointF(ctrl1_x, ctrl1_y),
            QPointF(ctrl2_x, ctrl2_y),
            self.target_pos
        )

        self.setPath(path)
