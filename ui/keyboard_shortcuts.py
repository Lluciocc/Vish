# keyboard_shortcuts.py
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QScroller,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.debug import Info
from core.icons import Icon
from core.traduction import Traduction
from themes.theme_manager import Theme

SHORTCUTS = {
    "general": {
        "title": ("general", "General"),
        "items": [
            {
                "description": ("shortcut_save_graph", "Save graph"),
                "shortcuts": [["Ctrl", "S"]],
            },
            {
                "description": ("shortcut_load_graph", "Load graph"),
                "shortcuts": [["Ctrl", "O"]],
            },
            {
                "description": ("shortcut_generate_bash", "Generate Bash script"),
                "shortcuts": [["Ctrl", "G"]],
            },
            {
                "description": ("shortcut_run_bash", "Run Bash script"),
                "shortcuts": [["Ctrl", "R"]],
            },
            {
                "description": ("shortcut_welcome_window", "Open welcome window"),
                "shortcuts": [["Ctrl", "W"]],
            },
            {
                "description": ("shortcut_toggle_fullscreen", "Toggle full screen"),
                "shortcuts": [["F11"]],
            },
            {
                "description": ("shortcut_open_settings", "Open settings"),
                "shortcuts": [["F9"]],
            },
            {
                "description": ("shortcut_save_log_file", "Save log file"),
                "shortcuts": [["Ctrl", "Alt", "L"]],
            },
        ],
    },
    "edition": {
        "title": ("edition", "Edition"),
        "items": [
            {
                "description": ("shortcut_copy_selection", "Copy selection"),
                "shortcuts": [["Ctrl", "C"]],
            },
            {"description": ("shortcut_paste", "Paste"), "shortcuts": [["Ctrl", "V"]]},
            {
                "description": ("shortcut_cut_selection", "Cut selection"),
                "shortcuts": [["Ctrl", "X"]],
            },
            {"description": ("shortcut_undo", "Undo"), "shortcuts": [["Ctrl", "Z"]]},
            {
                "description": ("shortcut_redo", "Redo"),
                "shortcuts": [["Ctrl", "Shift", "Z"], ["Ctrl", "Y"]],
            },
            {
                "description": ("shortcut_select_all", "Select all nodes"),
                "shortcuts": [["Ctrl", "A"]],
            },
            {
                "description": ("shortcut_duplicate", "Duplicate selection"),
                "shortcuts": [["Ctrl", "D"]],
            },
            {
                "description": ("shortcut_delete", "Delete selected nodes"),
                "shortcuts": [["Del"]],
            },
            {
                "description": (
                    "shortcut_node_palette",
                    "Open node palette for selected node",
                ),
                "shortcuts": [["Ctrl", "Space"]],
            },
        ],
    },
    "graph": {
        "title": ("graph", "Graph"),
        "items": [
            {
                "description": ("shortcut_reconnection_mode", "Reconnection mode"),
                "shortcuts": [["Ctrl", "LB"]],
            },
            {
                "description": ("shortcut_removing_mode", "Removing mode"),
                "shortcuts": [["Alt", "LB"]],
            },
            {
                "description": ("shortcut_reset_zoom", "Reset zoom"),
                "shortcuts": [["Ctrl", "MB"]],
            },
            {
                "description": ("shortcut_comment_box", "Create comment box"),
                "shortcuts": [["C"]],
            },
            {
                "description": ("shortcut_auto_layout", "Auto layout graph"),
                "shortcuts": [["F"]],
            },
            {
                "description": ("shortcut_rebuild_graph", "Rebuild graph"),
                "shortcuts": [["R"]],
            },
            {"description": ("shortcut_frame_all", "Frame all"), "shortcuts": [["H"]]},
            {
                "description": (
                    "shortcut_temporary_translation",
                    "Temporary translation (hold Alt)",
                ),
                "shortcuts": [["Alt"]],
            },
            {"description": ("shortcut_zoom_in", "Zoom in"), "shortcuts": [["Num+"]]},
            {"description": ("shortcut_zoom_out", "Zoom out"), "shortcuts": [["Num-"]]},
        ],
    },
}

KEY_SIZE = 24
KEY_SPACING = 6
ROW_SPACING = 8
ENTRY_SPACING = 2
DESCRIPTION_SHORTCUT_SPACING = 10
DESCRIPTION_MIN_WIDTH = 120
DESCRIPTION_TARGET_WIDTH = 180
COLUMN_MIN_WIDTH = DESCRIPTION_TARGET_WIDTH + 100
COLUMN_MAX_WIDTH = COLUMN_MIN_WIDTH * 2
COLUMN_SPACING = 24
CATEGORY_SPACING = 22
SCROLL_FADE_HEIGHT = 18
DEFAULT_KEY_STYLE = {
    "icon": "keycap_common",
    "width": 1,
    "show_label": True,
}

KEY_STYLES = {
    "Ctrl": {"icon": "keycap_large", "width": 2},
    "Shift": {"icon": "keycap_large", "width": 2},
    "Space": {"icon": "keycap_large", "width": 2},
    "Alt": {"icon": "keycap_large", "width": 2},
    "Num+": {"icon": "keycap_large", "width": 2},
    "Num-": {"icon": "keycap_large", "width": 2},
    "LB": {"icon": "mouse_left", "width": 1, "show_label": False},
    "MB": {"icon": "mouse_middle", "width": 1, "show_label": False},
    "RB": {"icon": "mouse_right", "width": 1, "show_label": False},
    "Mouse": {"icon": "mouse_simple", "width": 1, "show_label": False},
}


def get_key_style(key):
    return KEY_STYLES.get(key, DEFAULT_KEY_STYLE)


def get_key_width(key, size=KEY_SIZE):
    return int(get_key_style(key)["width"] * size)


def get_shortcut_width(keys, size=KEY_SIZE, spacing=KEY_SPACING):
    if not keys:
        return 0

    key_widths = sum(get_key_width(key, size) for key in keys)
    return key_widths + spacing * (len(keys) - 1)


def get_shortcut_area_width():
    return max(
        get_shortcut_width(keys)
        for section in SHORTCUTS.values()
        for item in section["items"]
        for keys in item["shortcuts"]
    )


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        child_layout = item.layout()
        widget = item.widget()
        if child_layout is not None:
            _clear_layout(child_layout)
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()


class KeyImage(QSvgWidget):
    def __init__(self, key, size, parent=None):
        super().__init__(parent)
        style = get_key_style(key)
        width = get_key_width(key, size)

        Icon.load_widget(self, "shortcuts", style["icon"], width, size)
        self.setFixedSize(width, size)


class ShortcutKey(QWidget):
    def __init__(self, key, size=KEY_SIZE):
        super().__init__()
        style = get_key_style(key)
        width = get_key_width(key, size)
        self.setFixedSize(width, size)

        self.image = KeyImage(key, size, self)
        self.image.move(0, 0)

        if not style.get("show_label", True):
            return

        self.key_label = QLabel(key, self)
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setFixedSize(width, size)
        self.key_label.setStyleSheet(
            f"color: {Theme.get_color('SHORTCUTS-LABEL_TEXT_INVERT')}"
        )


class ShortcutRow(QWidget):
    def __init__(self, keys, description, key_area_width):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(DESCRIPTION_SHORTCUT_SPACING)

        if description:
            text = QLabel(description)
            text.setWordWrap(True)
            text.setMinimumWidth(DESCRIPTION_MIN_WIDTH)
            text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            text.setStyleSheet(
                f"font-size: 15px; color: {Theme.get_color('SHORTCUTS-LABEL_DESCRIPTION')}"
            )
            layout.addWidget(text, 1, Qt.AlignVCenter)
        else:
            spacer = QWidget()
            spacer.setMinimumWidth(DESCRIPTION_MIN_WIDTH)
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(spacer, 1)

        key_container = QWidget()
        key_container.setFixedWidth(key_area_width)
        key_container.setFixedHeight(KEY_SIZE)

        key_layout = QHBoxLayout(key_container)
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.setSpacing(KEY_SPACING)
        key_layout.setAlignment(Qt.AlignLeft)

        for key in keys:
            key_layout.addWidget(ShortcutKey(key))

        layout.addWidget(key_container, 0, Qt.AlignRight | Qt.AlignVCenter)


class ShortcutEntry(QWidget):
    def __init__(self, item, key_area_width):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ENTRY_SPACING)

        description = Traduction.get_trad(*item["description"])
        for index, keys in enumerate(item["shortcuts"]):
            row_description = description if index == 0 else ""
            layout.addWidget(ShortcutRow(keys, row_description, key_area_width))


class ShortcutColumn(QWidget):
    def __init__(self, section, key_area_width):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, -10)
        layout.setSpacing(ROW_SPACING)

        label = QLabel(Traduction.get_trad(*section["title"]))
        layout.addWidget(label)

        title_bar = QWidget()
        title_bar.setFixedHeight(2)
        layout.addWidget(title_bar)

        for item in section["items"]:
            layout.addWidget(ShortcutEntry(item, key_area_width))

        label.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {Theme.get_color('SHORTCUTS-LABEL_TITLE')};"
        )
        title_bar.setStyleSheet(
            f"background-color: {Theme.get_color('SHORTCUTS-SEPARATOR')}; border-radius: 1px;"
        )


class ResponsiveShortcutsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.key_area_width = get_shortcut_area_width()
        self.column_count = 1
        self.row_count = 1
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.base_layout = QHBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)

        self.category_count = len(SHORTCUTS)
        self.stacks = []

        for section in SHORTCUTS.values():
            self.stacks.append(self.create_stack(section))
        for index in range(self.category_count):
            self.base_layout.addLayout(self.create_column_space())

    def create_column_space(self):
        layout = QVBoxLayout()
        layout.addSpacing(ROW_SPACING)
        layout.setContentsMargins(0, 0, 0, 0)

        shrink_widget = QWidget()
        shrink_widget.setFixedSize(0, 0)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(shrink_widget)
        return layout

    def create_stack(self, section):
        stack = ShortcutColumn(section, self.key_area_width)
        stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        return stack

    def resizeEvent(self, event):
        max_columns = int((event.size().width() - 24) / COLUMN_MIN_WIDTH)

        if self.column_count != max_columns:
            if max_columns <= self.category_count:
                self.column_count = max_columns
                self.row_count = max(
                    int(round(self.category_count / self.column_count)), 1
                )
                self.format_grid()

    def format_grid(self):
        grid = []
        for column in range(self.column_count):
            for row in range(self.row_count):
                grid.append([column, row])

        for index in range(len(self.stacks)):
            self.base_layout.children()[grid[index][0]].insertWidget(
                grid[index][1], self.stacks[index]
            )


class ScrollFade(QWidget):
    def __init__(self, edge, parent=None):
        super().__init__(parent)
        self.edge = edge
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setFixedHeight(SCROLL_FADE_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)
        base = QColor(Theme.get_color("SHORTCUTS-BACKGROUND"))
        solid = QColor(base)
        solid.setAlpha(230)
        transparent = QColor(base)
        transparent.setAlpha(0)

        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.edge == "top":
            gradient.setColorAt(0, solid)
            gradient.setColorAt(1, transparent)
        else:
            gradient.setColorAt(0, transparent)
            gradient.setColorAt(1, solid)
        painter.fillRect(self.rect(), gradient)


class ShortcutScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(scroll_style())

        self.top_fade = ScrollFade("top", self.viewport())
        self.bottom_fade = ScrollFade("bottom", self.viewport())
        self.verticalScrollBar().rangeChanged.connect(self._update_fades)
        self.verticalScrollBar().valueChanged.connect(self._update_fades)

        try:
            QScroller.grabGesture(
                self.viewport(), QScroller.ScrollerGestureType.TouchGesture
            )
        except AttributeError:
            QScroller.grabGesture(self.viewport(), QScroller.TouchGesture)

        self._update_fades()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_fades()
        self._update_fades()

    def _position_fades(self):
        width = self.viewport().width()
        height = self.viewport().height()
        self.top_fade.setGeometry(0, 0, width, SCROLL_FADE_HEIGHT)
        self.bottom_fade.setGeometry(
            0, max(0, height - SCROLL_FADE_HEIGHT), width, SCROLL_FADE_HEIGHT
        )
        self.top_fade.raise_()
        self.bottom_fade.raise_()

    def _update_fades(self, *args):
        scrollbar = self.verticalScrollBar()
        maximum = scrollbar.maximum()
        value = scrollbar.value()
        self.top_fade.setVisible(maximum > 0 and value > 0)
        self.bottom_fade.setVisible(maximum > 0 and value < maximum)


class KeyboardShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            Traduction.get_trad("keyboard_shortcuts", "Keyboard Shortcuts")
        )
        self.setModal(True)
        self.setMinimumSize(360, 294)
        if Info.get_device_type() == "phone":
            self.showMaximized()
        else:
            self.resize(980, 560)

        self.setStyleSheet(
            f"QDialog {{background: {Theme.get_color('SHORTCUTS-BACKGROUND')}}}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = ShortcutScrollArea()
        scroll.setWidget(ResponsiveShortcutsWidget())
        root.addWidget(scroll)


def scroll_style() -> str:
    return f"""
            QScrollArea {{
                background: {Theme.get_color("SCROLL_AREA")};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: {Theme.get_color("SCROLL_SUB_BAR")};
            }}
            QScrollBar:vertical {{
                width: 10px;
                margin: 2px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.get_color("SCROLL_HANDLE")};
                min-height: 34px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.get_color("SCROLL_HANDLE_HOVER")};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: {Theme.get_color("SCROLL_SUB_BAR")};
            }}
        """
