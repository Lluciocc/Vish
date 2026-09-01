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

from themes.theme_manager import Theme


class Style:
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

    def toolpanels_style() -> str:
        return f"""
                    background: {Theme.get_color("MAIN-PPANALS_BACKGROUND")};
                    color: {Theme.get_color("MAIN-TOOLPANELS_TEXT")};
                    selection-background-color: {Theme.get_color("MAIN-TOOLPANELS_SELECT_BACKGROUND")};
            """
