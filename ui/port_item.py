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

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsTextItem

from core.graph import Port
from core.config import Config
from core.port_types import PORT_STYLES, PortStyle, PortType
from themes.theme_manager import Theme


TYPE = {
    PortType.EXEC: "",
    PortType.STRING: "STR",
    PortType.INT: "INT",
    PortType.BOOL: "BOOL",
    PortType.CONDITION: "CON",
    PortType.PATH: "PATH",
    PortType.VARIABLE: "VAR",
    PortType.ANY: "ANY",
}


FILTER = [
    "exec",
    "string",
    "int",
    "bool",
    "condition",
    "path",
    "variable",
    "any",
    "value",
    "result",
    "input",
    "output",
]


SIZE = 12
TWICE_SIZE = 2 * SIZE


class PortItem(QGraphicsItem):
    def __init__(self, port: Port, parent=None, is_input=False):
        self.style = PORT_STYLES[port.port_type]

        super().__init__(parent)

        self.port = port
        self.is_input = is_input
        self.edges = []
        self.parent = parent

        self.brush_color = self.style.color
        self.pen_color = Theme.get_color("PORT_ITEM-BORDER")
        self.highlight = False

        self.type_text = QGraphicsTextItem("", self)
        self.name = QGraphicsTextItem("", self)
        self.setup_port()

    def setup_port(self):
        self.overwrite_text_color(self.brush_color)
        self.name.setAcceptHoverEvents(False)
        self.name.setDefaultTextColor(Theme.get_color("PORT_ITEM-NAME"))
        self.setup_port_name()

    def setup_port_name(self):
        name_allowed = True
        for filter in FILTER:
            if self.port.name.lower() == filter:
                name_allowed = False
                break
        if name_allowed:
            if self.parent.node.collapsed == False:
                self.name.setPlainText(self.port.name)
            else:
                self.name.setPlainText("")

    def calculate_required_space(self):
        type_space = self.type_text.document().idealWidth() + 10
        required_width = self.type_text.document().idealWidth() + self.name.document().idealWidth()
        if self.is_input:
            self.type_text.setPos(10, -13)
            if self.type_text.toPlainText():
                self.name.setPos(type_space, -13)
            else:
                self.name.setPos(10, -13)
            if required_width > self.parent.width_input:
                self.parent.width_input = required_width
        else:
            self.type_text.setPos(-10 - self.type_text.document().idealWidth(), -13)
            if self.type_text.toPlainText():
                self.name.setPos(-self.name.document().idealWidth() - type_space, -13)
            else:
                self.name.setPos(-self.name.document().idealWidth() - 10, -13)
            if required_width > self.parent.width_output:
                self.parent.width_output = required_width

    def boundingRect(self):
        if self.port.port_type == PortType.EXEC or Config.PORT_HINT == False or self.parent.node.collapsed == True:
            if self.is_input:
                rect = QRectF(-SIZE, -SIZE, TWICE_SIZE, TWICE_SIZE)
            else:
                rect = QRectF(-SIZE, -SIZE, TWICE_SIZE, TWICE_SIZE)
        else:
            if self.is_input:
                rect = QRectF(-SIZE, -SIZE, self.type_text.document().idealWidth() + TWICE_SIZE, TWICE_SIZE)
            else:
                rect = QRectF(-self.type_text.document().idealWidth() - SIZE, -SIZE, self.type_text.document().idealWidth() + TWICE_SIZE, TWICE_SIZE)
        return rect

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(self.brush_color))
        painter.setPen(QPen(QColor(self.pen_color), 2))

        retval = QPainterPath()
        match self.port.port_type:
            # Exec: triangular arrow
            case PortType.EXEC:
                half = SIZE * 0.6
                shift = SIZE * 0.1
                retval.moveTo(-half + shift, -half)
                retval.lineTo(shift, -half)
                retval.lineTo(half + shift, 0)
                retval.lineTo(shift, half)
                retval.lineTo(-half + shift, half)
                retval.closeSubpath()
            # Default path
            case _:
                half = SIZE / 2
                retval.addEllipse(-half, -half, SIZE, SIZE)
                retval.closeSubpath()

        painter.drawPath(retval)

        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(10)
        self.setToolTip(self.port.tooltip)

    def overwrite_color(self, color):
        if color == "invalid":
            self.brush_color = Theme.get_color("PORT_ITEM-FILL_INVALID")
            if self.highlight:
                self.pen_color = Theme.get_color("PORT_ITEM-FILL_INVALID")
                self.overwrite_text_color("PORT_ITEM-FILL_INVALID", True)
            else:
                self.overwrite_text_color("PORT_ITEM-FILL_INVALID")
        elif color == "hover_enter":
            self.highlight = True
            self.pen_color = Theme.get_color("PORT_ITEM-BORDER_HOVER")
            self.overwrite_text_color(self.brush_color, True)
        elif color == "hover_leave":
            self.highlight = False
            self.pen_color = Theme.get_color("PORT_ITEM-BORDER")
            self.overwrite_text_color(self.brush_color)
        elif QColor.isValidColor(str(color)):
            self.brush_color = color
            self.overwrite_text_color(self.brush_color)
        else:  # reset
            self.brush_color = self.style.color
            self.overwrite_text_color(self.brush_color)
            if self.highlight:
                self.pen_color = Theme.get_color("PORT_ITEM-BORDER_RESET")
            else:
                self.pen_color = Theme.get_color("PORT_ITEM-BORDER")
        self.update()

    def overwrite_text_color(self, color, underscore = False):
        if  Config.PORT_HINT == True and self.parent.node.collapsed == False:
            if underscore:
                self.type_text.setHtml(f'<u><strong><div style="color: {color}">{TYPE[self.port.port_type]}</div></strong></u>')
            else:
                self.type_text.setHtml(f'<strong><div style="color: {color}">{TYPE[self.port.port_type]}</div></strong>')
        else:
            self.type_text.setHtml("")
        if not self.is_input:
            self.type_text.setPos(-10 - self.type_text.document().idealWidth(), -13)
        self.update()

    def center_scene_pos(self):
        if self.port.port_type == PortType.EXEC or Config.PORT_HINT == False or self.parent.node.collapsed == True:
            if self.is_input:
                return self.mapToScene(self.boundingRect().center() - QPointF(5, 0))
            else:
                return self.mapToScene(self.boundingRect().center() + QPointF(5, 0))
        else:
            text_size_adjustment = QPointF((self.type_text.document().idealWidth()) / 2 + 5, 0)
            if self.is_input:
                return self.mapToScene(self.boundingRect().center() - text_size_adjustment)
            else:
                return self.mapToScene(self.boundingRect().center() + text_size_adjustment)

    def hoverEnterEvent(self, event):
        self.overwrite_color("hover_enter")
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.overwrite_color("hover_leave")
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.scene().start_connection(self)
        event.accept()

    def mouseReleaseEvent(self, event):
        scene = self.scene()
        if scene:
            scene.end_connection(self)
        event.accept()
