from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QFrame, QWidget, QLineEdit, QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, QPropertyAnimation, Property, Signal
from PySide6.QtGui import QPainter, QColor
from core.config import Config, ConfigManager
from core.traduction import Traduction
from theme.theme import set_dark_theme, set_purple_theme, set_white_theme, Theme
from theme.theme_parser import load_theme, import_theme, delete_theme, theme_list, BUILTIN_THEMES, _themes_dir, parse_yaml
from ui.menu_style import apply_menu_style, apply_btn_style
from core.debug import Debug

def set_config_bool(attr_name: str, value: bool) -> None:
    if not hasattr(Config, attr_name):
        raise AttributeError(f"Config has no attribute '{attr_name}'")
    setattr(Config, attr_name, bool(value))
    ConfigManager.save_config()

def add_separator(layout: QVBoxLayout) -> None:
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
    sep.setStyleSheet("color: #d0d0d0;")
    layout.addWidget(sep)

def create_switch_row(label_key: str, fallback: str, config_attr: str):
    row = QHBoxLayout()
    label = QLabel(Traduction.get_trad(label_key, fallback))
    switch = Switch(getattr(Config, config_attr))
    switch.toggled.connect(lambda value: set_config_bool(config_attr, value))
    row.addWidget(label)
    row.addStretch()
    row.addWidget(switch)
    return row, label

_BUILTIN_SETTERS = {
    "dark": set_dark_theme,
    "purple": set_purple_theme,
    "white": set_white_theme,
}

class SettingsDialog(QDialog):
    traduction_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(380)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        self._build_appearance_section()
        add_separator(self.layout)
        self._build_language_section()
        add_separator(self.layout)
        self._build_advanced_section()
        self._build_footer()

        self.refresh_ui_texts()

    def make_section_title(self, key: str, fallback: str) -> QLabel:
        label = QLabel(Traduction.get_trad(key, fallback))
        label.setStyleSheet("font-weight: bold;")
        return label

    def _build_appearance_section(self):
        self.appearance_title = self.make_section_title("appearance", "Appearance")
        self.layout.addWidget(self.appearance_title)

        self.theme_combo = QComboBox()
        self._populate_theme_combo()
        self.theme_combo.setCurrentIndex(self.theme_combo.findData(Config.theme))
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)

        self.theme_label = QLabel(Traduction.get_trad("theme", "Theme"))

        self.import_theme_btn = QPushButton(Traduction.get_trad("import_theme", "Import…"))
        self.delete_theme_btn = QPushButton(Traduction.get_trad("delete_theme", "Delete"))
        self.import_theme_btn.clicked.connect(self.on_import_theme)
        self.delete_theme_btn.clicked.connect(self.on_delete_theme)
        self._refresh_delete_btn_state()

        row = QHBoxLayout()
        row.addWidget(self.theme_label)
        row.addStretch()
        row.addWidget(self.theme_combo)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.import_theme_btn)
        btn_row.addWidget(self.delete_theme_btn)
        btn_row.addStretch()

        self.layout.addLayout(row)
        self.layout.addLayout(btn_row)

    def _build_language_section(self):
        self.language_title = self.make_section_title("language", "Language")
        self.layout.addWidget(self.language_title)

        self.lang_combo = QComboBox()
        for label, code in [
            ("English", "en"), ("Francais", "fr"), ("Español", "es"),
            ("العربية", "ar"), ("Italiano", "it"), ("Deutsch", "de"),
            ("Português (Brasil)", "ptbr"),
        ]:
            self.lang_combo.addItem(label, code)

        self.lang_combo.setCurrentIndex(self.lang_combo.findData(Config.lang))
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)

        self.language_label = QLabel(Traduction.get_trad("language", "Language"))

        row = QHBoxLayout()
        row.addWidget(self.language_label)
        row.addStretch()
        row.addWidget(self.lang_combo)
        self.layout.addLayout(row)

    def _build_advanced_section(self):
        self._switches = []
        self.advanced_title = self.make_section_title("advanced", "Advanced")
        self.layout.addWidget(self.advanced_title)

        self.shebang_label = QLabel(Traduction.get_trad("custom_shebang", "Custom Shebang"))
        self.shebang_input = QLineEdit(Config.CUSTOM_SHEBANG)
        self.shebang_input.editingFinished.connect(self.on_shebang_changed)

        shebang_row = QHBoxLayout()
        shebang_row.addWidget(self.shebang_label)
        shebang_row.addStretch()
        shebang_row.addWidget(self.shebang_input)
        self.layout.addLayout(shebang_row)

        for key, fallback, attr in [
            ("debug", "Debug mode", "DEBUG"),
            ("using_tty", "Use TTY", "USING_TTY"),
            ("sync_nodes_and_gen", "Sync Nodes and Generation", "SYNC_NODES_AND_GEN"),
            ("auto_save", "Auto Save", "AUTO_SAVE"),
        ]:
            row, label = create_switch_row(key, fallback, attr)
            switch = row.itemAt(row.count() - 1).widget()  #  get the switch we just created
            self._switches.append(switch)
            setattr(self, f"{attr.lower()}_row",   row)
            setattr(self, f"{attr.lower()}_label", label)
            self.layout.addLayout(row)

    def _build_footer(self):
        self.layout.addStretch()
        footer = QHBoxLayout()
        footer.addStretch()
        self.close_btn = QPushButton()
        self.close_btn.clicked.connect(self.accept)
        footer.addWidget(self.close_btn)
        self.layout.addLayout(footer)

    def _populate_theme_combo(self):
        self.theme_combo.clear()
        builtin_labels = {
            "dark": ("theme_dark", "Dark"),
            "purple": ("theme_purple", "Purple"),
            "white": ("theme_white", "White"),
        }
        for name in theme_list:
            if name in builtin_labels:
                key, fallback = builtin_labels[name]
                self.theme_combo.addItem(Traduction.get_trad(key, fallback), name)
            else:
                self.theme_combo.addItem(name, name)

    def _refresh_delete_btn_state(self):
        current = self.theme_combo.currentData()
        self.delete_theme_btn.setEnabled(current not in BUILTIN_THEMES)

    def on_theme_changed(self):
        theme = self.theme_combo.currentData()
        if not theme or theme == Config.theme:
            return

        Config.theme = theme
        ConfigManager.save_config()

        setter = _BUILTIN_SETTERS.get(theme)
        if setter:
            setter()
        else:
            for file in _themes_dir().glob("*.yml"):
                try:
                    data = parse_yaml(file.read_text(encoding="utf-8"))
                    if data.get("name") == theme:
                        load_theme(str(file))
                        break
                except Exception:
                    Debug.Error(f"Failed to load theme from {file.name}")

        ConfigManager.save_config()
        self._refresh_delete_btn_state()
        self._propagate_theme_change()

    def on_import_theme(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "", "YAML Theme Files (*.yml *.yaml)"
        )
        if not path:
            return
        theme = import_theme(path)
        if theme is None:
            QMessageBox.critical(self, "Error", "Failed to import theme.")
            return
        self._populate_theme_combo()
        idx = self.theme_combo.findData(theme.selected_theme)
        if idx != -1:
            self.theme_combo.setCurrentIndex(idx)

    def on_delete_theme(self):
        name = self.theme_combo.currentData()
        if name in BUILTIN_THEMES:
            return
        reply = QMessageBox.question(
            self, "Delete Theme",
            f"Delete theme \"{name}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.No:
            return
        delete_theme(name)
        self._populate_theme_combo()
        self.theme_combo.setCurrentIndex(self.theme_combo.findData(Config.theme))

    def on_lang_changed(self):
        lang = self.lang_combo.currentData()
        if not lang or lang == Config.lang:
            return
        Config.lang = lang
        Traduction.set_translate_model(lang)
        ConfigManager.save_config()
        self.traduction_changed.emit()
        self.refresh_ui_texts()

    def on_shebang_changed(self):
        new_value = self.shebang_input.text().strip()
        if not new_value:
            self.shebang_input.setText(Config.CUSTOM_SHEBANG)
            return
        if new_value == Config.CUSTOM_SHEBANG:
            return
        reply = QMessageBox.warning(
            self, "Warning",
            "Changing the shebang may break script execution on some systems.\n\n"
            "Are you sure you know what you are doing?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.No:
            self.shebang_input.setText(Config.CUSTOM_SHEBANG)
            return
        Config.CUSTOM_SHEBANG = new_value
        ConfigManager.save_config()

    def _propagate_theme_change(self):
        p = self.parent()
        if p:
            p.graph_view.apply_theme()
            apply_menu_style(p.more_menu)
            apply_btn_style(p.more_btn)
            p.refresh_ui_texts()

        # Update switches
        for switch in getattr(self, "_switches", []):
            switch.update()

    def refresh_ui_texts(self):
        self.setWindowTitle(Traduction.get_trad("settings", "Settings"))

        self.appearance_title.setText(Traduction.get_trad("appearance", "Appearance"))
        self.language_title.setText(Traduction.get_trad("language", "Language"))
        self.advanced_title.setText(Traduction.get_trad("advanced", "Advanced"))
        self.theme_label.setText(Traduction.get_trad("theme", "Theme"))
        self.language_label.setText(Traduction.get_trad("language", "Language"))
        self.shebang_label.setText(Traduction.get_trad("custom_shebang", "Custom Shebang"))
        self.close_btn.setText(Traduction.get_trad("close", "Close"))
        self.import_theme_btn.setText(Traduction.get_trad("import_theme", "Import…"))
        self.delete_theme_btn.setText(Traduction.get_trad("delete_theme", "Delete"))

        for attr, key, fallback in [
            ("debug", "debug", "Debug mode"),
            ("using_tty", "using_tty", "Use TTY"),
            ("sync_nodes_and_gen", "sync_nodes_and_gen", "Sync Nodes and Generation"),
            ("auto_save", "auto_save", "Auto Save"),
        ]:
            label = getattr(self, f"{attr}_label", None)
            if label:
                label.setText(Traduction.get_trad(key, fallback))

        for data_val, key, fallback in [
            ("dark", "theme_dark", "Dark"),
            ("purple", "theme_purple", "Purple"),
            ("white", "theme_white", "White"),
        ]:
            idx = self.theme_combo.findData(data_val)
            if idx != -1:
                self.theme_combo.setItemText(idx, Traduction.get_trad(key, fallback))

        if self.parent():
            self.parent().refresh_ui_texts()

class Switch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 22)
        self._checked = checked
        self._offset = 20 if checked else 2

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animate()
        self.toggled.emit(self._checked)

    def _animate(self):
        self.anim = QPropertyAnimation(self, b"offset", self)
        self.anim.setDuration(150)
        self.anim.setStartValue(self._offset)
        self.anim.setEndValue(20 if self._checked else 2)
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(Theme.ACCENT) if self._checked else QColor("#b0b0b0"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 42, 22, 11, 11)
        painter.setBrush(Qt.white)
        painter.drawEllipse(self._offset, 2, 18, 18)

    def getOffset(self) -> int:
        return self._offset

    def setOffset(self, value: int):
        self._offset = value
        self.update()

    offset = Property(int, getOffset, setOffset)