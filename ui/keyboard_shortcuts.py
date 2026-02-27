import os
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from core.traduction import Traduction
from theme.theme import Theme
from core.debug import Info


SHORTCUTS = {
    "general": {
        "title": ("general", "General"),
        "items": [
            (["ctrl", "s"], "shortcut_save_graph"),
            (["ctrl", "o"], "shortcut_load_graph"),
            (["ctrl", "g"], "shortcut_generate_bash"),
            (["ctrl", "r"], "shortcut_run_bash"),
        ],
    },
    "edition": {
        "title": ("edition", "Edition"),
        "items": [
            (["ctrl", "c"], "shortcut_copy_selection"),
            (["ctrl", "v"], "shortcut_paste"),
            (["ctrl", "x"], "shortcut_cut_selection"),
            (["ctrl", "z"], "shortcut_undo"),
            (["ctrl", "shift", "z"], "shortcut_redo_1"),
            (["ctrl", "y"], "shortcut_redo_2"),
            (["ctrl", "a"], "shortcut_select_all"),
            (["ctrl", "d"], "shortcut_duplicate"),
            (["del"], "shortcut_delete"),
            (["ctrl", "space"], "shortcut_node_palette"),
        ],
    },
    "graph": {
        "title": ("graph", "Graph"),
        "items": [
            (["c"], "shortcut_comment_box"),
            (["f"], "shortcut_auto_layout"),
            (["r"], "shortcut_rebuild_graph"),
            (["h"], "shortcut_frame_all")
        ],
    },
}


class KeyImage(QLabel):
    def __init__(self, key):
        super().__init__()
        path = Info.resource_path(f"assets/icons/keyboard/{key}.png")
        if not os.path.exists(path):
            path = Info.resource_path(f"assets/icons/keyboard/unknown.png")
        pix = QPixmap(path)
        pix.setDevicePixelRatio(2)
        # pix = pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pix)
        self.setFixedSize(40, 40)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent;")


class ShortcutRow(QWidget):
    def __init__(self, keys, label):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(6)

        for i, key in enumerate(keys):
            layout.addWidget(KeyImage(key))
            if i < len(keys) - 1:
                plus = QLabel("+")
                plus.setStyleSheet(f"color: {Theme.TEXT}; font-size: 15px; background: transparent;")
                layout.addWidget(plus)

        layout.addSpacing(16)

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
                col.layout.addWidget(ShortcutRow(keys, text))
            col.layout.addStretch()
            content.addWidget(col)

        root.addLayout(content)
