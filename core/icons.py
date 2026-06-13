# icons.py
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

from PySide6.QtSvgWidgets import QGraphicsSvgItem, QSvgWidget
from PySide6.QtGui import QIcon
from theme.theme import Theme
from core.debug import Info
import os


class Path:  
    @staticmethod
    def get_path(category, icon_name):
        category = category.lower().replace(" ", "_")
        icon_name = icon_name.lower().replace(" ", "_")

        contrast = Theme.type
        icon_path = Info.resource_path(f"assets/icons/{category}/{icon_name}.svg")
        if not os.path.exists(icon_path):
            icon_path = Info.resource_path(f"assets/icons/{category}/{contrast}/{icon_name}.svg")
            if not os.path.exists(icon_path):
                icon_path = Info.resource_path(f"assets/icons/{category}/{icon_name}_placeholder.svg")
                if not os.path.exists(icon_path):
                    icon_path = Info.resource_path(f"assets/icons/{category}/{contrast}/{icon_name}_placeholder.svg")
                    if not os.path.exists(icon_path):
                        icon_path = Info.resource_path("assets/icons/placeholder.svg")
        return icon_path


class Icon:
    @staticmethod
    def load_icon(category, name):
        icon_path = Path.get_path(category, name)
        icon = QIcon(icon_path)
        return icon

    @staticmethod
    def load_item(self, category, name, size, padding):
        icon_path = Path.get_path(category, name)
        icon = QGraphicsSvgItem(icon_path, self)

        bounds = icon.boundingRect()
        scale = size / max(bounds.width(), bounds.height())
        icon.setScale(scale)
        icon_y = (self.HEADER_HEIGHT - bounds.height() * scale) / 2
        icon.setPos(padding, icon_y)

    @staticmethod
    def load_widget(self, category, name, width, height):
        icon_path = Path.get_path(category, name)
        icon = QSvgWidget(icon_path, self)
        icon.setFixedSize(width, height)
