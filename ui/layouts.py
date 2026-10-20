# toolbar.py
#
# Copyright 2026 Ick
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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter

from core.config import Config, ConfigManager
from themes.theme_manager import Theme


class Layout(QSplitter):
    def __init__(self, editor):
        super().__init__()

        self.editor = editor

        self.handle_width = 12
        self.setHandleWidth(self.handle_width)
        self.sub_splitter = QSplitter()
        self.sub_splitter.setHandleWidth(self.handle_width)
        self.output_splitter = QSplitter()
        self.output_splitter.setHandleWidth(self.handle_width)
        self.output_splitter.setStyleSheet(apply_bash_textedit_style())

        self.set_layout()

    def set_layout(self):
        layout = Config.LAYOUT[0]
        mirror_horizontal = Config.LAYOUT[1]
        mirror_vertical = Config.LAYOUT[2]
        height = self.height()
        width = self.width()

        match layout:
            case "phone":
                height_small = height / 4
                height_medium = height / 2
                height_tall = height_small * 3

                self.output_splitter.setOrientation(Qt.Vertical)
                self.sub_splitter.setOrientation(Qt.Vertical)
                self.setOrientation(Qt.Vertical)

                self.output_splitter.setSizes([height / 8 - self.handle_width, height / 8 - self.handle_width])
                if mirror_vertical:
                    self.output_splitter.insertWidget(0, self.editor.run_output_text)
                    self.output_splitter.insertWidget(1, self.editor.output_text)

                    self.sub_splitter.insertWidget(0, self.editor.property_panel)
                    self.sub_splitter.insertWidget(1, self.editor.graph_view)

                    self.insertWidget(0, self.output_splitter)
                    self.insertWidget(1, self.sub_splitter)

                    self.setSizes([height_small - self.handle_width, height_tall - self.handle_width])
                    self.sub_splitter.setSizes([height_small - self.handle_width, height_medium - self.handle_width])
                    if not self.editor.run_output_text.isVisible():
                        self.output_splitter.setSizes([0, 1])
                else:
                    self.output_splitter.insertWidget(0, self.editor.output_text)
                    self.output_splitter.insertWidget(1, self.editor.run_output_text)

                    self.sub_splitter.insertWidget(0, self.editor.graph_view)
                    self.sub_splitter.insertWidget(1, self.editor.property_panel)

                    self.insertWidget(0, self.sub_splitter)
                    self.insertWidget(1, self.output_splitter)

                    self.setSizes([height_tall - self.handle_width, height_small - self.handle_width])
                    self.sub_splitter.setSizes([height_medium - self.handle_width, height_small - self.handle_width])
                    if not self.editor.run_output_text.isVisible():
                        self.output_splitter.setSizes([1, 0])

            case "viewport_wide":
                width_small = width / 3
                width_tall = width_small * 2
                height_small = height / 4
                height_tall = height_small * 3

                self.output_splitter.setOrientation(Qt.Horizontal)
                self.sub_splitter.setOrientation(Qt.Horizontal)
                self.setOrientation(Qt.Vertical)

                self.output_splitter.setSizes([width_small - self.handle_width, width_small - self.handle_width])
                if mirror_horizontal:
                    self.output_splitter.insertWidget(0, self.editor.run_output_text)
                    self.output_splitter.insertWidget(1, self.editor.output_text)

                    self.sub_splitter.insertWidget(0, self.output_splitter)
                    self.sub_splitter.insertWidget(1, self.editor.property_panel)

                    self.sub_splitter.setSizes([width_tall - self.handle_width, width_small - self.handle_width])
                    if not self.editor.run_output_text.isVisible():
                        self.output_splitter.setSizes([0, 1])
                else:
                    self.output_splitter.insertWidget(0, self.editor.output_text)
                    self.output_splitter.insertWidget(1, self.editor.run_output_text)

                    self.sub_splitter.insertWidget(0, self.editor.property_panel)
                    self.sub_splitter.insertWidget(1, self.output_splitter)

                    self.sub_splitter.setSizes([width_small - self.handle_width, width_tall - self.handle_width])
                    if not self.editor.run_output_text.isVisible():
                        self.output_splitter.setSizes([1, 0])

                if mirror_vertical:
                    self.insertWidget(0, self.sub_splitter)
                    self.insertWidget(1, self.editor.graph_view)
                    self.setSizes([height_small, height_tall])
                else:
                    self.insertWidget(0, self.editor.graph_view)
                    self.insertWidget(1, self.sub_splitter)
                    self.setSizes([height_tall, height_small])

            case "frame":
                width_small = width / 5
                width_tall = width_small * 4
                height_small = height / 4
                height_tall = height_small * 3

                self.output_splitter.setOrientation(Qt.Horizontal)
                self.sub_splitter.setOrientation(Qt.Horizontal)
                self.setOrientation(Qt.Vertical)

                self.output_splitter.insertWidget(0, self.editor.output_text)
                self.output_splitter.insertWidget(1, self.editor.run_output_text)

                if mirror_horizontal:
                    self.sub_splitter.insertWidget(0, self.editor.graph_view)
                    self.sub_splitter.insertWidget(1, self.editor.property_panel)
                    self.sub_splitter.setSizes([width_tall, width_small])
                else:
                    self.sub_splitter.insertWidget(0, self.editor.property_panel)
                    self.sub_splitter.insertWidget(1, self.editor.graph_view)
                    self.sub_splitter.setSizes([width_small, width_tall])

                if mirror_vertical:
                    self.insertWidget(0, self.output_splitter)
                    self.insertWidget(1, self.sub_splitter)
                    self.setSizes([height_small, height_tall])
                else:
                    self.insertWidget(0, self.sub_splitter)
                    self.insertWidget(1, self.output_splitter)
                    self.setSizes([height_tall, height_small])

                if not self.editor.run_output_text.isVisible():
                    self.output_splitter.setSizes([1, 0])

            case "center":
                width_small = width / 5
                width_tall = width_small * 3

                self.output_splitter.setOrientation(Qt.Vertical)
                self.sub_splitter.setOrientation(Qt.Horizontal)
                self.setOrientation(Qt.Horizontal)

                self.sub_splitter.setParent(None)
                self.output_splitter.insertWidget(0, self.editor.output_text)
                self.output_splitter.insertWidget(1, self.editor.run_output_text)

                if mirror_horizontal:
                    self.insertWidget(0, self.output_splitter)
                    self.insertWidget(1, self.editor.graph_view)
                    self.insertWidget(2, self.editor.property_panel)
                    self.setSizes([width_small, width_tall, width_small])
                else:
                    self.insertWidget(0, self.editor.property_panel)
                    self.insertWidget(1, self.editor.graph_view)
                    self.insertWidget(2, self.output_splitter)
                    self.setSizes([width_small, width_tall, width_small])

                self.output_splitter.setSizes([height * 0.7, height * 0.3])
                if not self.editor.run_output_text.isVisible():
                    self.output_splitter.setSizes([1, 0])

            case _:
                width_small = width / 5
                width_medium = width_small * 2
                width_tall = width_small * 3

                self.output_splitter.setOrientation(Qt.Vertical)
                self.sub_splitter.setOrientation(Qt.Horizontal)
                self.setOrientation(Qt.Horizontal)

                self.output_splitter.insertWidget(0, self.editor.output_text)
                self.output_splitter.insertWidget(1, self.editor.run_output_text)

                if mirror_horizontal:
                    self.sub_splitter.insertWidget(0, self.output_splitter)
                    self.sub_splitter.insertWidget(1, self.editor.property_panel)

                    self.insertWidget(0, self.sub_splitter)
                    self.insertWidget(1, self.editor.graph_view)
                    self.setSizes([width_medium, width_tall])
                else:
                    self.sub_splitter.insertWidget(0, self.editor.property_panel)
                    self.sub_splitter.insertWidget(1, self.output_splitter)

                    self.insertWidget(0, self.editor.graph_view)
                    self.insertWidget(1, self.sub_splitter)
                    self.setSizes([width_tall, width_medium])

                self.sub_splitter.setSizes([width_small, width_small])
                self.output_splitter.setSizes([height * 0.7, height * 0.3])
                if not self.editor.run_output_text.isVisible():
                    self.output_splitter.setSizes([1, 0])

    def _apply_theme(self):
        self.output_splitter.setStyleSheet(apply_bash_textedit_style())


def apply_bash_textedit_style() -> str:
    return f"""
                background: {Theme.get_color("MAIN-BASHPANEL_BACKGROUND")};
                border: 1px solid {Theme.get_color("MAIN-BASHPANEL_BORDER")};
        """
