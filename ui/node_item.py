# node_item.py
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


from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem

from core.graph import Node
from core.icons import Icon
from core.traduction import Traduction
from nodes.registry import NODE_REGISTRY
from themes.theme_manager import Theme
from ui.port_item import PortItem


class NodeItem(QGraphicsItem):
    DEFAULT_WIDTH = 180
    MIN_WIDTH = 36
    HEADER_HEIGHT = 34
    PORT_SPACING = 24
    NODE_HEIGHT_SPACING = 15
    ICON_SIZE = 24

    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.port_items = {}
        self.icon_item = None
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.title_item = QGraphicsTextItem(
            Traduction.get_trad(node.node_type, node.title), self
        )
        self.title_item.setDefaultTextColor(QColor(Theme.get_color("NODE_ITEM-TITLE")))
        self.title_item.setPos(10, 8)
        self.setZValue(1)
        self.collapsable = NODE_REGISTRY.get(self.node.node_type)["collapsable"]

        self.width_input = 0
        self.width_output = 0
        self.width = self.DEFAULT_WIDTH
        self.setup_icon()
        self.setup_ports()

        min_header_width = self.title_item.document().idealWidth() + self.ICON_SIZE + self.MIN_WIDTH
        min_body_width = self.width_input + self.width_output + self.MIN_WIDTH
        if self.DEFAULT_WIDTH < min_header_width:
            self.width = min_header_width
        if self.width < min_body_width:
            self.width = min_body_width
        if self.width != self.DEFAULT_WIDTH:
            for port_id in self.port_items:
                port_item = self.port_items[port_id]
                if not port_item.is_input:
                    y_pos = port_item.y()
                    port_item.setPos(self.width, y_pos)

        if self.node.collapsed == False:
            body_height = self.calc_height(True)
        else:
            body_height = 0
        self.height = self.HEADER_HEIGHT + body_height

    def update_traduction(item: Node, language):
        Traduction.set_translate_model(language)
        item.title_item.setPlainText(
            Traduction.get_trad(item.node.node_type, item.node.title)
        )

    def get_pos_y(self):
        if self.node.collapsed == True:
            return self.PORT_SPACING * 2 - self.HEADER_HEIGHT / 2
        else:
            return 0

    def setup_ports(self):
        for i, port in enumerate(self.node.inputs):
            port_item = PortItem(port, self, is_input=True)
            y_pos = (i + 2) * self.PORT_SPACING
            port_item.setPos(0, y_pos)
            self.port_items[port.id] = port_item

        for i, port in enumerate(self.node.outputs):
            port_item = PortItem(port, self, is_input=False)
            y_pos = (i + 2) * self.PORT_SPACING
            port_item.setPos(self.width, y_pos)
            self.port_items[port.id] = port_item

    def boundingRect(self):
        return QRectF(0, self.get_pos_y(), self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 8, 8)

        if self.isSelected():
            painter.setPen(QPen(QColor(Theme.get_color("NODE_ITEM-BORDER_HOVER")), 3))
        else:
            painter.setPen(QPen(QColor(Theme.get_color("NODE_ITEM-BORDER")), 2))

        painter.setBrush(QBrush(QColor(Theme.get_color("NODE_ITEM-BACKGROUND"))))
        painter.drawPath(path)

        header_rect = QRectF(0, self.get_pos_y(), self.width, self.HEADER_HEIGHT)
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
                self.scene().auto_save_triggered.emit()
                scene.views()[0].update()

            self.node.x = value.x()
            self.node.y = value.y()

        elif change == QGraphicsItem.ItemSelectedChange and value:
            scene = self.scene()
            if scene and hasattr(scene, "_z_counter"):
                self.setZValue(scene._z_counter)
                self.node.z = scene._z_counter
                scene._z_counter += 1

        return super().itemChange(change, value)

    def get_port_scene_pos(self, port_id: str) -> QPointF:
        if port_id in self.port_items:
            port_item = self.port_items[port_id]
            return self.mapToScene(port_item.pos())
        return QPointF()

    def mousePressEvent(self, event):
        scene = self.scene()
        if event.type() == 158 and event.buttons() == Qt.LeftButton: # left double click
            if self.collapsable == True:
                self.node.collapsed = not self.node.collapsed
                self.switch_collapse()

        if scene:
            scene.node_selected.emit(self.node)

            if hasattr(scene, "_z_counter"):
                self.setZValue(scene._z_counter)
                self.node.z = scene._z_counter
                scene._z_counter += 1

        super().mousePressEvent(event)

    def switch_collapse(self):
        scene = self.scene()
        for port_id in self.port_items:
            port_item = self.port_items[port_id]
            port_item.overwrite_text_color(port_item.brush_color)

            if self.node.collapsed:
                body_height = 0
            else:
                body_height = self.calc_height(True)

        self.height = self.HEADER_HEIGHT + body_height
        scene.update_edges_for_node(self)
        scene.update()
        self.setup_icon()

    def calc_height(self, body=False):
        body_height = (
            max(
                len(self.node.inputs) * self.PORT_SPACING,
                len(self.node.outputs) * self.PORT_SPACING,
            )
            + self.NODE_HEIGHT_SPACING
        )
        if body == True:
            return body_height
        self.height = self.HEADER_HEIGHT + body_height

    def get_icon_node(self, item: Node, padding):
        node = NODE_REGISTRY.get(item.node_type)
        if node is not None:
            if not self.icon_item:
                self.icon_item = Icon.load_item(
                    self, f"nodes/{node['category']}", item.title
                )
            bounds = self.icon_item.boundingRect()
            scale = self.ICON_SIZE / max(bounds.width(), bounds.height())
            self.icon_item.setScale(scale)
            icon_y = (self.HEADER_HEIGHT - bounds.height() * scale) / 2 + self.get_pos_y()
            self.icon_item.setPos(padding, icon_y)

    def setup_icon(self):
        icon_size = 24
        if self.node.collapsed == False:
            padding = 6
        else:
            padding = 10
        self.get_icon_node(self.node, padding)

        text_x = self.ICON_SIZE + padding
        text_rect = self.title_item.boundingRect()
        text_y = (self.HEADER_HEIGHT - text_rect.height()) / 2 + self.get_pos_y()
        self.title_item.setPos(text_x, text_y)
