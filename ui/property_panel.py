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

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
)


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

        self.layout.addWidget(QLabel(f"<b>{node.title}</b>"))

        for key, value in node.properties.items():

            if key.startswith("DYNAMIC_"):
                label = key.replace("DYNAMIC_", "").replace("_", " ").title()

                button = QPushButton(label)
                button.clicked.connect(
                    lambda _, k=key: self._run_dynamic(k)
                )

                self.layout.addWidget(button)
                continue

            label = QLabel(key)
            field = QLineEdit(str(value))

            field.textChanged.connect(
                lambda v, k=key: self._update_property(k, v)
            )

            self.layout.addWidget(label)
            self.layout.addWidget(field)

        self.layout.addStretch()

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
