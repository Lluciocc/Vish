# property_panel.py
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

from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from themes.theme_manager import Theme


class PropertyPanel(QWidget):
    def __init__(self, parent=None, graph_view=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setMinimumWidth(250)
        self.current_node = None
        self.graph_view = graph_view

    def set_node(self, node):
        self.clear()
        self.current_node = node

        if not node:
            return

        self.title = QLabel(f"<b>{node.title}</b>")
        self.layout.addWidget(self.title)

        for key, value in node.properties.items():

            if key.startswith("DYNAMIC_"):
                self.label = key.replace("DYNAMIC_", "").replace("_", " ").title()

                self.button = QPushButton(label)
                self.button.clicked.connect(
                    lambda _, k=key: self._run_dynamic(k)
                )

                self.layout.addWidget(self.button)
                continue

            self.label = QLabel(key)
            self.field = QLineEdit(str(value))

            self.field.textChanged.connect(
                lambda v, k=key: self._update_property(k, v)
            )

            self.layout.addWidget(self.label)
            self.layout.addWidget(self.field)

        self.layout.addStretch()
        self._apply_theme()

    def _update_property(self, key, value):
        if self.current_node:
            self.current_node.properties[key] = value

    def _run_dynamic(self, key):
        if not self.current_node:
            return

        func_name = key.replace("DYNAMIC_", "")
        func = getattr(self.current_node, func_name, None)

        if callable(func):
            func()

            node_item = self.graph_view.node_items.get(self.current_node.id)
            if node_item:
                node_item.rebuild_ports()

            self.graph_view.graph_scene.graph_changed.emit()

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _apply_theme(self):
        if self.findChild(QLabel):
            self.title.setStyleSheet(f"color: {Theme.get_color("PROPERTY_PANEL-TITLELABEL_TEXT")}")
        for widget in self.layout.parent().children():
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {Theme.get_color("PROPERTY_PANEL-LABEL_TEXT")}")
            elif isinstance(widget, QPushButton):
                widget.setStyleSheet(pushbutton_style())
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet(lineedit_style())


def lineedit_style() -> str:
    return f"""
            QLineEdit {{
                color: {Theme.get_color("PROPERTY_PANEL-LINEEDIT_TEXT")};
                border: 1px solid {Theme.get_color("PROPERTY_PANEL-LINEEDIT_BORDER")};
                border-radius: 5px;
                padding: 3px 5px;
                background: {Theme.get_color("PROPERTY_PANEL-LINEEDIT_BACKGROUND")};
                selection-background-color: {Theme.get_color("PROPERTY_PANEL-LINEEDIT_SELECTION")};
                selection-color: {Theme.get_color("PROPERTY_PANEL-LINEEDIT_SELECTION_TEXT")};
            }}
            QLineEdit:hover {{
                border: 1px solid {Theme.get_color("PROPERTY_PANEL-LINEEDIT_BORDER_HOVER")};
            }}
        """

def pushbutton_style() -> str:
    return f"""
            QPushButton {{
                color: {Theme.get_color("PROPERTY_PANEL-PUSHBUTTON_TEXT")};
                border: 1px solid {Theme.get_color("PROPERTY_PANEL-PUSHBUTTON_BORDER")};
                border-radius: 5px;
                min-width: 60px;
                padding: 3px 5px;
                background: {Theme.get_color("PROPERTY_PANEL-PUSHBUTTON_BACKGROUND")};
            }}
            QPushButton:focus,
            QPushButton:selected,
            QPushButton:hover {{
                border-color: {Theme.get_color("PROPERTY_PANEL-PUSHBUTTON_BORDER_HOVER")};
                background: {Theme.get_color("PROPERTY_PANEL-PUSHBUTTON_BACKGROUND_HOVER")};
                outline: none;
            }}
        """
