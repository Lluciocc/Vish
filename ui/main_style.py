# main_style.py
#
# Copyright 2026 Lluciocc, Ick
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

from core.icons import Icon
from PySide6.QtWidgets import QPushButton
from themes.theme_manager import Theme
import os


class Style:
    def apply_menu_style() -> str:
        return f"""
            QMenu {{
                background: {Theme.get_color("MAIN-MENU_BACKGROUND")};
                color: {Theme.get_color("MAIN-MENU_TEXT")};
                border-radius: 12px;
                padding: 8px;
                border: 1px solid {Theme.get_color("MAIN-MENU_BORDER")};
                font-size: 14px;
            }}
            QMenu::icon {{
                padding: 0px 0px 0px 15px;
            }}
            QMenu::item {{
                padding: 10px 5px 10px 15px;
                border-radius: 8px;
                min-width: 150px;
            }}
            QMenu::item:selected {{
                background: {Theme.get_color("MAIN-MENU_ITEM_SELECTION")};
            }}
            QMenu::separator {{
                height: 1px;
                background: {Theme.get_color("MAIN-MENU_SEPARATOR")};
                margin: 8px 10px;
            }}
        """

    def apply_button_style() -> str:
        return f"""
                QToolButton {{
                    color: {Theme.get_color("MAIN-BUTTON_TEXT")};
                    border: 1px solid {Theme.get_color("MAIN-BUTTON_BORDER")};
                    font-size: 15px;
                    padding: 4px 8px;
                        border-radius: 5px;
                }}
                QToolButton:focus,
                QToolButton:selected,
                QToolButton:hover {{
                    background: {Theme.get_color("MAIN-BUTTON_BACKGROUND_HOVER")};
                    border: 1px solid {Theme.get_color("MAIN-BUTTON_BORDER_HOVER")};
                }}
                QToolButton::menu-indicator {{
                    image: none;
                }}
            """

    def apply_bash_textedit_style() -> str:
        return f"""
                    background: {Theme.get_color("MAIN-BASHPANEL_BACKGROUND")};
                    border: 1px solid {Theme.get_color("MAIN-BASHPANEL_BORDER")};
            """

    def apply_viewport_style() -> str:
        return f"""
                QGraphicsView {{
                    background: {Theme.get_color("MAIN-BASHPANEL_BACKGROUND")};
                    border: 1px solid {Theme.get_color("MAIN-BASHPANEL_BORDER")};
                }}
            """

    def pushbutton_style() -> str:
        return f"""
                QPushButton {{
                    color: {Theme.get_color("MAIN-PUSHBUTTON_TEXT")};
                    border: 1px solid {Theme.get_color("MAIN-PUSHBUTTON_BORDER")};
                    border-radius: 5px;
                    min-width: 60px;
                    padding: 3px 5px;
                    background: {Theme.get_color("MAIN-PUSHBUTTON_BACKGROUND")};
                }}
                QPushButton:focus,
                QPushButton:selected,
                QPushButton:hover {{
                    border-color: {Theme.get_color("MAIN-PUSHBUTTON_BORDER_HOVER")};
                    background: {Theme.get_color("MAIN-PUSHBUTTON_BACKGROUND_HOVER")};
                    outline: none;
                }}
            """

    def toolpanels_style() -> str:
        return f"""
                    background: {Theme.get_color("MAIN-TOOLPANALS_BACKGROUND")};
                    color: {Theme.get_color("MAIN-TOOLPANELS_TEXT")};
                    selection-background-color: {Theme.get_color("MAIN-TOOLPANELS_SELECT_BACKGROUND")};
            """

    def apply_icon_for_button(button, name):
        icon = Icon.load_icon("menu_app", name)
        button.setIcon(icon)
        if isinstance(button, QPushButton):
            button.setStyleSheet(Style.pushbutton_style())
            button.setFixedHeight(34)
