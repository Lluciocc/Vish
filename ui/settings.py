from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QFrame, QWidget, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, Property, Signal
from PySide6.QtGui import QPainter, QColor
from core.config import Config, ConfigManager
from core.traduction import Traduction
from theme.theme import set_dark_theme, set_purple_theme, set_white_theme
from ui.menu_style import apply_menu_style, apply_btn_style

def set_config_bool(attr_name: str, value: bool):
    if not hasattr(Config, attr_name):
        raise AttributeError(f"Config has no attribute '{attr_name}'")
    setattr(Config, attr_name, bool(value))
    ConfigManager.save_config()


def add_separator(layout: QVBoxLayout):
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
    sep.setStyleSheet("color: #d0d0d0;")
    layout.addWidget(sep)


def create_switch_row(label_key, fallback, config_attr):
    row = QHBoxLayout()

    label = QLabel(Traduction.get_trad(label_key, fallback))
    switch = Switch(getattr(Config, config_attr))

    switch.toggled.connect(
        lambda value: set_config_bool(config_attr, value)
    )

    row.addWidget(label)
    row.addStretch()
    row.addWidget(switch)

    return row, label

class SettingsDialog(QDialog):
    traduction_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setModal(True)
        self.setFixedWidth(360)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        self._build_appearance_section()
        add_separator(self.layout)
        self._build_language_section()
        add_separator(self.layout)
        self._build_advanced_section()
        self._build_footer()

        self.refresh_ui_texts()

    def make_section_title(self, key, fallback):
        label = QLabel(Traduction.get_trad(key, fallback))
        label.setStyleSheet("font-weight: bold;")
        return label

    def _build_appearance_section(self):
        self.appearance_title = self.make_section_title(
            "appearance", "Appearance"
        )
        self.layout.addWidget(self.appearance_title)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(
            Traduction.get_trad("theme_dark", "Dark"), "dark"
        )
        self.theme_combo.addItem(
            Traduction.get_trad("theme_purple", "Purple"), "purple"
        )
        self.theme_combo.addItem(
            Traduction.get_trad("theme_white", "White"), "white"
        )

        self.theme_combo.setCurrentIndex(
            self.theme_combo.findData(Config.theme)
        )
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)

        self.theme_label = QLabel(
            Traduction.get_trad("theme", "Theme")
        )

        row = QHBoxLayout()
        row.addWidget(self.theme_label)
        row.addStretch()
        row.addWidget(self.theme_combo)

        self.layout.addLayout(row)

    def _build_language_section(self):
        self.language_title = self.make_section_title(
            "language", "Language"
        )
        self.layout.addWidget(self.language_title)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem(
            Traduction.get_trad("lang_en", "English"), "en"
        )
        self.lang_combo.addItem(
            Traduction.get_trad("lang_fr", "French"), "fr"
        )
        self.lang_combo.addItem(
            Traduction.get_trad("lang_es", "Spanish"), "es"
        )
        self.lang_combo.addItem(
            Traduction.get_trad("lang_ar", "Arabic"), "ar"
        )
        self.lang_combo.addItem(
            Traduction.get_trad("lang_it", "Italian"), "it"
        )
        self.lang_combo.addItem(
            Traduction.get_trad("lang_de", "German"), "de"
        )

        self.lang_combo.setCurrentIndex(
            self.lang_combo.findData(Config.lang)
        )
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)

        self.language_label = QLabel(
            Traduction.get_trad("language", "Language")
        )

        row = QHBoxLayout()
        row.addWidget(self.language_label)
        row.addStretch()
        row.addWidget(self.lang_combo)

        self.layout.addLayout(row)

    def _build_advanced_section(self):
        self.advanced_title = self.make_section_title(
            "advanced", "Advanced"
        )
        self.layout.addWidget(self.advanced_title)

        self.debug_row, self.debug_label = create_switch_row(
            "debug", "Debug mode", "DEBUG"
        )
        self.layout.addLayout(self.debug_row)

        self.tty_row, self.tty_label = create_switch_row(
            "using_tty", "Use TTY", "USING_TTY"
        )
        self.sync_row, self.sync_label = create_switch_row(
            "sync_nodes_and_gen", "Sync Nodes and Generation", "SYNC_NODES_AND_GEN"
        )
        self.auto_save_row, self.auto_save_label = create_switch_row(
            "auto_save", "Auto Save", "AUTO_SAVE"
        )
        self.shebang_label = QLabel(
            Traduction.get_trad("custom_shebang", "Custom Shebang")
        )

        self.shebang_input = QLineEdit()
        self.shebang_input.setText(Config.CUSTOM_SHEBANG)
        self.shebang_input.editingFinished.connect(self.on_shebang_changed)

        shebang_row = QHBoxLayout()
        shebang_row.addWidget(self.shebang_label)
        shebang_row.addStretch()
        shebang_row.addWidget(self.shebang_input)

        self.layout.addLayout(shebang_row)
        self.layout.addLayout(self.tty_row)
        self.layout.addLayout(self.sync_row)
        self.layout.addLayout(self.auto_save_row)

    def _build_footer(self):
        self.layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()

        self.close_btn = QPushButton()
        self.close_btn.clicked.connect(self.accept)

        footer.addWidget(self.close_btn)
        self.layout.addLayout(footer)

    def on_theme_changed(self):
        theme = self.theme_combo.currentData()
        if not theme or theme == Config.theme:
            return

        Config.theme = theme
        ConfigManager.save_config()

        if theme == "dark":
            set_dark_theme()
        elif theme == "purple":
            set_purple_theme()
        elif theme == "white":
            set_white_theme()

        if self.parent():
            self.parent().graph_view.apply_theme()
            apply_menu_style(self.parent().more_menu)
            apply_btn_style(self.parent().more_btn)
            self.parent().refresh_ui_texts()

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
            self,
            "Warning",
            "Changing the shebang may break script execution on some systems.\n\n"
            "Are you sure you know what you are doing?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            self.shebang_input.setText(Config.CUSTOM_SHEBANG)
            return

        Config.CUSTOM_SHEBANG = new_value
        ConfigManager.save_config()

    def update_combo_item(self, combo, data, key, fallback):
        index = combo.findData(data)
        if index != -1:
            combo.setItemText(index, Traduction.get_trad(key, fallback))

    def refresh_ui_texts(self):
        self.setWindowTitle(
            Traduction.get_trad("settings", "Settings")
        )

        self.appearance_title.setText(
            Traduction.get_trad("appearance", "Appearance")
        )
        self.language_title.setText(
            Traduction.get_trad("language", "Language")
        )
        self.advanced_title.setText(
            Traduction.get_trad("advanced", "Advanced")
        )

        self.theme_label.setText(
            Traduction.get_trad("theme", "Theme")
        )
        self.language_label.setText(
            Traduction.get_trad("language", "Language")
        )

        self.debug_label.setText(
            Traduction.get_trad("debug", "Debug mode")
        )
        self.tty_label.setText(
            Traduction.get_trad("using_tty", "Use TTY")
        )
        self.sync_label.setText(
            Traduction.get_trad("sync_nodes_and_gen", "Sync Nodes and Generation")
        )
        self.auto_save_label.setText(
            Traduction.get_trad("auto_save", "Auto Save")
        )

        self.close_btn.setText(
            Traduction.get_trad("close", "Close")
        )
        self.shebang_label.setText(
            Traduction.get_trad("custom_shebang", "Custom Shebang")
        )

        self.update_combo_item(self.theme_combo, "dark", "theme_dark", "Dark")
        self.update_combo_item(self.theme_combo, "purple", "theme_purple", "Purple")
        self.update_combo_item(self.theme_combo, "white", "theme_white", "White")

        self.update_combo_item(self.lang_combo, "en", "lang_en", "English")
        self.update_combo_item(self.lang_combo, "fr", "lang_fr", "French")
        self.update_combo_item(self.lang_combo, "es", "lang_es", "Spanish")
        self.update_combo_item(self.lang_combo, "ar", "lang_ar", "Arabic")
        self.update_combo_item(self.lang_combo, "it", "lang_it", "Italian")
        self.update_combo_item(self.lang_combo, "de", "lang_de", "German")

        if self.parent():
            self.parent().refresh_ui_texts()

class Switch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 22)
        self._checked = checked
        self._offset = 20 if checked else 2

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animate()
        self.toggled.emit(self._checked)

    def _animate(self):
        start = self._offset
        end = 20 if self._checked else 2

        self.anim = QPropertyAnimation(self, b"offset", self)
        self.anim.setDuration(150)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        bg = QColor("#3584e4" if self._checked else "#b0b0b0")
        painter.setBrush(bg)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 42, 22, 11, 11)

        painter.setBrush(Qt.white)
        painter.drawEllipse(self._offset, 2, 18, 18)

    def getOffset(self):
        return self._offset

    def setOffset(self, value):
        self._offset = value
        self.update()

    offset = Property(int, getOffset, setOffset)
