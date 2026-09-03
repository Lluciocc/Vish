# theme_manager.py
#
# Copyright 2026 Ick, Lluciocc
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

from pathlib import Path

from PySide6.QtGui import QColor, QGuiApplication

from core.config import Config
from core.debug import Debug, Info
from core.logger import Logger


class Theme:
    colors = {}
    fallback_colors = {}
    theme = None
    theme_names = []
    language = ""
    author = ""
    description = ""
    comment_labels = ""
    icons = "dark"

    @staticmethod
    def get_data():
        if Theme.theme != Config.theme:
            Theme.theme = Config.theme
            theme_path = Theme.get_path(Theme.theme)
            if theme_path == None:
                return
            if "_" in Theme.theme:
                fallback_theme_path = Theme.get_fallback_path(theme_path)
                if fallback_theme_path == None:
                    return

                with open(fallback_theme_path) as fallback_theme_data:
                    Theme.fallback_colors = Theme.parse_yaml(fallback_theme_data.read())
            with open(theme_path) as theme_data:
                Theme.colors = Theme.parse_yaml(theme_data.read())

            Theme.icons = Theme.colors.get("icons")
            if Theme.icons == None:
                Theme.icons = Theme.fallback_colors.get("icons")

            Theme.author = Theme.colors.get("author")
            if Theme.author == None:
                Theme.author = "Unknown"

            if Theme.language != Config.lang:
                Theme.language = Config.lang
                Theme.comment_labels = Theme.colors.get("comment_labels").get(Theme.language.upper())
                if Theme.comment_labels == None:
                    Theme.comment_labels = Theme.colors.get("comment_labels").get("EN")

            if Theme.colors.get("description") != None:
                Theme.description = Theme.colors.get("description").get(Theme.language.upper())
                if Theme.description == None:
                    Theme.description = Theme.colors.get("description").get("EN")
                    if Theme.description == None:
                        Theme.description = ""
            Logger.LogMessage(f"THEME_MANAGER: Theme {Theme.theme} loaded.")

    @staticmethod
    def get_color(selector):
        Theme.get_data()

        color = Theme.colors.get("theme_detail").get(selector)
        if color == None:
            color = Theme.fallback_colors.get("theme_detail").get(selector)
            if color == None:
                return None

        if QColor.isValidColor(str(color)):
            return color
        if color.split("-")[0] == "ACCENT":
            color = Theme.apply_accent_alpha(color)
            return color
        fallback_color = Theme.colors.get("theme_main").get(color)
        if QColor.isValidColor(str(fallback_color)):
            return fallback_color
        if fallback_color.split("-")[0] == "ACCENT":
            color = Theme.apply_accent_alpha(fallback_color)
            return color
        fallback_color = Theme.fallback_colors.get("theme_main").get(color)
        if QColor.isValidColor(str(fallback_color)):
            return fallback_color
        if fallback_color.split("-")[0] == "ACCENT":
            color = Theme.apply_accent_alpha(fallback_color)
            return color
        return None

    def apply_accent_alpha(color_code):
        color = QGuiApplication.palette().accent().color().name()

        alpha = 1
        if "-" in color_code:
            alpha = float(color_code.split("-")[1])
            if alpha != 1:
                alpha = int(round(alpha * 256 - 1))
                hex_alpha = f"{alpha:02x}"
                color = "#" + hex_alpha + color.split("#")[1]
        return color

    @staticmethod
    def get_properties(properties, selector):
        Theme.get_data()

        theme_property = Theme.colors.get(properties).get(selector)
        return theme_property

    @staticmethod
    def get_theme_names(theme_list, language, imported):
        if not imported:
            if language == Theme.language and Theme.theme_names:
                return Theme.theme_names

        Theme.theme_names.clear()
        Theme.language = language
        for theme in theme_list:
            path = Theme.get_path(theme)
            with open(path) as theme_data:
                theme_properties = Theme.parse_yaml(theme_data.read())
                name = theme_properties.get("name").get(language)
                if name == None:
                    name = theme_properties.get("name").get("EN")
                Theme.theme_names.append(name)
                Theme.comment_labels = theme_properties.get("comment_labels").get(Theme.language.upper())
                if Theme.comment_labels == None:
                    Theme.comment_labels = theme_properties.get("comment_labels").get("EN")
        return Theme.theme_names

    @staticmethod
    def get_path(theme) -> Path:
        path = Path(Info.resource_path(f"themes/{theme}"))
        if path.exists():
            return path

        path = Path(Info.get_config_path()) / "themes" / f"{theme}"
        if path.exists():
            return path

        path = Path(Info.resource_path("themes/dark.yml"))
        if path.exists():
            if Config.DEBUG:
                Debug.Warn("THEME_MANAGER: Custom theme not found! Loading standard theme.")
            return path
        themes_names = (Info.get_files_from_directory("resource_path", "themes/", ".yml"))
        for theme in themes_names:
            if "_" not in theme:
                path = Path(Info.resource_path(f"themes/{theme}"))
                if Config.DEBUG:
                    Debug.Warn("THEME_MANAGER: Custom theme not found! Standard Theme not found! Loading next available fallback theme.")
                return path
        print("\033[31m[ERROR] THEME_MANAGER: No theme found! -> Crash!")
        return None

    @staticmethod
    def get_fallback_path(theme_path) -> Path:
        if len(str(theme_path).rsplit("_")) > 1:
            fallback_theme = str(theme_path).rsplit("_")[1]
        else:
            fallback_theme = str(theme_path).rsplit("_")[0]

        path = Path(Info.resource_path(f"themes/{fallback_theme}"))
        if path.exists():
            return path

        themes_names = (Info.get_files_from_directory("resource_path", "themes/", ".yml"))
        for theme in themes_names:
            if "_" not in theme:
                path = Path(Info.resource_path(f"themes/{theme}"))
                if Config.DEBUG:
                    Debug.Warn("THEME_MANAGER: Missing fallback theme! Loading next available fallback theme.")
                return path

        print("\033[31m[ERROR] THEME_MANAGER: No fallback theme found! -> Crash!")
        return None

    @staticmethod
    def parse_yaml(text: str) -> dict:
        lines = text.splitlines()
        root: dict = {}
        stack: list[tuple[int, dict]] = [(-1, root)]

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            if " #" in stripped:
                stripped = stripped.split(" #", 1)[0]

            indent = len(raw_line) - len(raw_line.lstrip(" "))
            colon_idx = stripped.index(":")
            key = stripped[:colon_idx].strip()
            value_raw = stripped[colon_idx + 1:].strip()

            if value_raw and value_raw[0] in ('"', "'") and value_raw[-1] == value_raw[0]:
                value: object = value_raw[1:-1]
            elif not value_raw:
                value = None
            else:
                for cast in (int, float):
                    try:
                        value = cast(value_raw)
                        break
                    except ValueError:
                        pass
                else:
                    if value_raw.lower() == "true":
                        value = True
                    elif value_raw.lower() == "false":
                        value = False
                    else:
                        value = value_raw

            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()

            parent = stack[-1][1]

            if value is None:
                nested: dict = {}
                parent[key] = nested
                stack.append((indent, nested))
            else:
                parent[key] = value

        return root
