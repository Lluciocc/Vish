from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QFrame, QWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, Property, Signal
from PySide6.QtGui import QPainter, QColor
from core.config import Config
from core.traduction import Traduction
from theme.theme import set_dark_theme, set_purple_theme, set_white_theme

def set_config_bool(attr_name: str, value: bool):
    if not hasattr(Config, attr_name):
        raise AttributeError(f"Config has no attribute '{attr_name}'")
    setattr(Config, attr_name, bool(value))


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

    def _build_appearance_section(self):
        title = QLabel(Traduction.get_trad("appearance", "Appearance"))
        title.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(title)

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

        row = QHBoxLayout()
        row.addWidget(QLabel(Traduction.get_trad("theme", "Theme")))
        row.addStretch()
        row.addWidget(self.theme_combo)

        self.layout.addLayout(row)

    def _build_language_section(self):
        title = QLabel(Traduction.get_trad("language", "Language"))
        title.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(title)

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

        self.lang_combo.setCurrentIndex(
            self.lang_combo.findData(Config.lang)
        )
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)

        row = QHBoxLayout()
        row.addWidget(QLabel(Traduction.get_trad("language", "Language")))
        row.addStretch()
        row.addWidget(self.lang_combo)

        self.layout.addLayout(row)

    def _build_advanced_section(self):
        title = QLabel(Traduction.get_trad("advanced", "Advanced"))
        title.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(title)

        self.debug_row, self.debug_label = create_switch_row(
            "debug", "Debug mode", "DEBUG"
        )
        self.layout.addLayout(self.debug_row)

        self.tty_row, self.tty_label = create_switch_row(
            "using_tty", "Use TTY", "USING_TTY"
        )
        self.layout.addLayout(self.tty_row)


    def _build_footer(self):
        self.layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()

        self.close_btn = QPushButton(
            Traduction.get_trad("close", "Close")
        )
        self.close_btn.clicked.connect(self.accept)

        footer.addWidget(self.close_btn)
        self.layout.addLayout(footer)

    def on_theme_changed(self):
        theme = self.theme_combo.currentData()
        if not theme or theme == Config.theme:
            return

        Config.theme = theme

        if theme == "dark":
            set_dark_theme()
        elif theme == "purple":
            set_purple_theme()
        elif theme == "white":
            set_white_theme()

    def on_lang_changed(self):
        lang = self.lang_combo.currentData()
        if not lang or lang == Config.lang:
            return

        Config.lang = lang
        Traduction.set_translate_model(lang)

        self.refresh_ui_texts()

    def refresh_ui_texts(self):
        self.setWindowTitle(
            Traduction.get_trad("settings", "Settings")
        )

        self.close_btn.setText(
            Traduction.get_trad("close", "Close")
        )

        self.debug_label.setText(
            Traduction.get_trad("debug", "Debug mode")
        )
        self.tty_label.setText(
            Traduction.get_trad("using_tty", "Use TTY")
        )

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
