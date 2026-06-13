# menu_style.py
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

from theme.theme import Theme
from core.debug import Info
from core.icons import Icon
import os

def apply_menu_style(menu):
    menu.setStyleSheet(f"""
        QMenu {{
            background-color: {Theme.BACKGROUND};
            color: {Theme.TEXT};
            border-radius: 12px;
            padding: 8px;
            border: 1px solid {Theme.BUTTON_PRESSED};
            font-size: 14px;
        }}

        QMenu::item {{
            padding: 10px 22px;
            border-radius: 8px;
            min-width: 150px;
        }}

        QMenu::item:selected {{
            background-color: {Theme.BUTTON_HOVER};
        }}

        QMenu::separator {{
            height: 1px;
            background: {Theme.BUTTON_PRESSED};
            margin: 8px 10px;
        }}
    """)



def apply_btn_style(btn):
    btn.setStyleSheet(f"""
        QToolButton {{
            color: {Theme.TEXT};
            font-size: 18px;
            padding: 4px 8px;
            border-radius: 8px;
        }}
        QToolButton:hover {{
            background-color: {Theme.BUTTON_HOVER};
        }}
        QToolButton::menu-indicator {{
            image: none;
        }}
    """)

def apply_icon_for_btn(btn, name):
    icon = Icon.load_icon("menu_app", name)
    btn.setIcon(icon)
