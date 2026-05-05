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

KEY_SIZE = 24
KEY_SPACING = 6
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
        for keys, _ in section["items"]
    )


class KeyImage(QSvgWidget):
    def __init__(self, key, size, parent=None):
        super().__init__(parent)
        style = get_key_style(key)
        width = get_key_width(key, size)

        Icon.load_widget(self, "shortcuts", style["icon"], width, size)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(width, size)


class ShortcutKey(QWidget):
    def __init__(self, key, size=KEY_SIZE):
        super().__init__()
        style = get_key_style(key)
        width = get_key_width(key, size)
        self.setFixedSize(width, size)
        self.setStyleSheet("background: transparent;")

        self.image = KeyImage(key, size, self)
        self.image.move(0, 0)

        if not style.get("show_label", True):
            return

        self.key_label = QLabel(key, self)
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setFixedSize(width, size)
        self.key_label.setStyleSheet(f"background: transparent; color: {Theme.TEXT_INV};")


class ShortcutRow(QWidget):
    def __init__(self, keys, label, key_area_width):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(KEY_SPACING)

        key_container = QWidget()
        key_container.setFixedWidth(key_area_width)
        key_container.setStyleSheet("background: transparent;")

        key_layout = QHBoxLayout(key_container)
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.setSpacing(KEY_SPACING)
        key_layout.setAlignment(Qt.AlignLeft)

        for key in keys:
            key_layout.addWidget(ShortcutKey(key))

        layout.addWidget(key_container)

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

        key_area_width = get_shortcut_area_width()
        for section in SHORTCUTS.values():
            col = ShortcutColumn(Traduction.get_trad(*section["title"]))
            for keys, text in section["items"]:
                col.layout.addWidget(ShortcutRow(keys, text, key_area_width))
            col.layout.addStretch()
            content.addWidget(col)

        root.addLayout(content)
