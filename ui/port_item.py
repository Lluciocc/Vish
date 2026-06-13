# port_item.py
#
# Copyright 2026 Lluciocc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from core.graph import Port
from core.port_types import PortStyle, PORT_STYLES, PortType
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem


class PortItem(QGraphicsPathItem):
    def __init__(self, port: Port, parent=None, is_input=False):
        style = PORT_STYLES[port.port_type]

        super().__init__(self.generate_path(port, style), parent)

        self.port = port
        self.is_input = is_input
        self.edges = []

        self.setBrush(QBrush(QColor(style.color)))
        self.setPen(QPen(QColor("#2C3E50"), 2))

        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setZValue(10)
        # SET THE TOOLTIP
        self.setToolTip(self.port.tooltip)

        self.highlight = False

    def get_color(self) -> QColor:
        port_type = getattr(self.port, "type", None) or getattr(self.port, "port_type", None)
        style = PORT_STYLES.get(port_type)
        if style:
            return QColor(style.color)
        return QColor("#95A5A6")  

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
        # print("PORT CLICK")
        pass


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
