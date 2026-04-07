import os
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt
from core.traduction import Traduction
from theme.theme import Theme
from core.debug import Info
from core.icons import Icon


SHORTCUTS = {
    "general": {
        "title": ("general", "General"),
        "items": [
            (["Ctrl", "S"], "shortcut_save_graph"),
            (["Ctrl", "O"], "shortcut_load_graph"),
            (["Ctrl", "G"], "shortcut_generate_bash"),
            (["Ctrl", "R"], "shortcut_run_bash"),
            (["Ctrl", "W"], "shortcut_welcome_window"),
            (["F11"], "shortcut_toggle_fullscreen"),
            (["F9"], "shortcut_open_settings"),
            (["Ctrl", "Alt", "L"], "shortcut_save_log_file"),
        ],
    },
    "edition": {
        "title": ("edition", "Edition"),
        "items": [
            (["Ctrl", "C"], "shortcut_copy_selection"),
            (["Ctrl", "V"], "shortcut_paste"),
            (["Ctrl", "X"], "shortcut_cut_selection"),
            (["Ctrl", "Z"], "shortcut_undo"),
            (["Ctrl", "Shift", "Z"], "shortcut_redo_1"),
            (["Ctrl", "Y"], "shortcut_redo_2"),
            (["Ctrl", "A"], "shortcut_select_all"),
            (["Ctrl", "D"], "shortcut_duplicate"),
            (["Del"], "shortcut_delete"),
            (["Ctrl", "Space"], "shortcut_node_palette"),
        ],
    },
    "graph": {
        "title": ("graph", "Graph"),
        "items": [
            (["Ctrl", "LB"], "shortcut_reconnection_mode"),
            (["Alt", "LB"], "shortcut_removing_mode"),
            (["Ctrl", "MB"], "shortcut_reset_zoom"),
            (["C"], "shortcut_comment_box"),
            (["F"], "shortcut_auto_layout"),
            (["R"], "shortcut_rebuild_graph"),
            (["H"], "shortcut_frame_all"),
            (["Alt"], "shortcut_temporary_translation"),
            (["Num+"], "shortcut_zoom_in"),
            (["Num-"], "shortcut_zoom_out"),
        ],
    },
}


class KeyImage(QSvgWidget):
    def __init__(self, key, size):
        super().__init__()
        if key == "Ctrl" or key == "Shift" or key == "Space" or key == "Alt" or key == "Num+" or key == "Num-":
            width = 2 * size
            icon = "keycap_large"
        else:
            width = size
            icon = "keycap_common"

        icon = Icon.load_widget(self, "shortcuts", icon, width, size)
        self.setStyleSheet("background: transparent;")
        self.setMaximumSize(width, size)
        self.setMinimumSize(width, size)


class ShortcutRow(QWidget):
    def __init__(self, keys, label, category):
        super().__init__()
        key_size = 24
        spacing = 6
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(spacing)

        if category == ("general", "General"):
            spaceCount = 1
        elif category == ("edition", "Edition"):
            spaceCount = 2
        elif category == ("graph", "Graph"):
            spaceCount = 1

        for i, key in enumerate(keys):
            key_label = QLabel(key)
            key_label.setAlignment(Qt.AlignCenter)
            key_label.setStyleSheet(f"background: transparent; color: {Theme.TEXT_INV};")

            if key == "Ctrl" or key == "Shift" or key == "Space" or key == "Alt" or key == "Num+" or key == "Num-":
                layout.addWidget(KeyImage(key, key_size))
                key_label.setFixedWidth(key_size * 2)
                layout.addSpacing((key_size * 2 + spacing) * -1)
                layout.addWidget(key_label)
            elif spaceCount == i:
                layout.addWidget(KeyImage(key, key_size))
                key_label.setFixedWidth(key_size)
                layout.addSpacing((key_size + spacing) * -1)
                layout.addWidget(key_label)
                layout.addSpacing(key_size)
            else:
                layout.addSpacing(key_size / 2)
                layout.addWidget(KeyImage(key, key_size))
                key_label.setFixedWidth(key_size)
                layout.addSpacing((key_size + spacing) * -1)
                layout.addWidget(key_label)
                layout.addSpacing(key_size / 2)

        layout.addSpacing((spaceCount - i) * 54 - 12)
        text = QLabel(Traduction.get_trad(label, label))
        text.setStyleSheet(f"font-size: 15px; color: {Theme.TEXT}; background: transparent;")
        layout.addWidget(text)
        layout.addStretch()


class ShortcutColumn(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        label = QLabel(title)
        label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {Theme.TEXT}; background: transparent;")
        layout.addWidget(label)

        self.layout = layout


class KeyboardShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(Traduction.get_trad("keyboard_shortcuts", "Keyboard Shortcuts"))
        self.setModal(True)
        if Info.get_device_type() == "phone":
            self.showMaximized()
        else:
            self.resize(980, 560)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        header = QHBoxLayout()
        # title = QLabel(Traduction.get_trad("keyboard_shortcuts", "Keyboard Shortcuts"))
        # title.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {Theme.TEXT}; background: transparent;")
        # header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(56)

        for section in SHORTCUTS.values():
            col = ShortcutColumn(Traduction.get_trad(*section["title"]))
            for keys, text in section["items"]:
                col.layout.addWidget(ShortcutRow(keys, text, section["title"]))
            col.layout.addStretch()
            content.addWidget(col)

        root.addLayout(content)
