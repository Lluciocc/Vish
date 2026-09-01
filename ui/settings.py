# settings.py
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

from core.config import Config, ConfigManager
from core.debug import Debug, Info
from core.logger import Logger
from core.traduction import Traduction
from PySide6.QtCore import Property, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QComboBox, QDialog, QFileDialog, QFrame, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)
from themes.theme_manager import Theme
from ui.modal import Modal
import os
import shutil


def set_config_bool(attr_name: str, value: bool) -> None:
    if not hasattr(Config, attr_name):
        msg = f"Config has no attribute '{attr_name}'"
        Logger.LogError(msg)
        raise AttributeError(msg)
    setattr(Config, attr_name, bool(value))
    ConfigManager.save_config()

def add_separator(layout: QVBoxLayout) -> None:
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
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


class SettingsDialog(QDialog):
    traduction_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumSize(360, 294)
        if Info.get_device_type() == "phone":
            self.showMaximized()
        else:
            self.resize(380, 520)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)

        self.content_widget = QWidget()
        self.content_widget.setObjectName("SettingsContent")

        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(10, 10, 10, 2)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("SettingsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setWidget(self.content_widget)

        self.root_layout.addWidget(self.scroll_area)
        add_separator(self.root_layout)
        self.root_layout.setSpacing(11)

        self._build_appearance_section()
        add_separator(self.layout)
        self._build_language_section()
        add_separator(self.layout)
        self._build_advanced_section()
        self._build_footer()
        self._apply_theme()

    def make_section_title(self, key: str, fallback: str) -> QLabel:
        label = QLabel(Traduction.get_trad(key, fallback))
        label.setObjectName("SectionTitle")
        return label

    def _build_appearance_section(self):
        self.appearance_title = self.make_section_title("appearance", "Appearance")
        self.layout.addWidget(self.appearance_title)

        self.theme_combo = QComboBox()
        self.theme_combo.setMaxVisibleItems(16)
        self._populate_theme_combo(False)
        self.theme_combo.setCurrentIndex(self.theme_combo.findData(Theme.theme))
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.theme_combo.setPlaceholderText(Traduction.get_trad("unknown", "Unknown"))

        if Theme.author.count(" ") > 0:
            self.theme_author = QLabel(Traduction.get_trad("authors", "Authors"))
        else:
            self.theme_author = QLabel(Traduction.get_trad("author", "Author"))
        self.theme_title = QLabel(Traduction.get_trad("theme", "Theme"))
        self.theme_author_name = QLabel(Theme.author)
        self.theme_author_name.setObjectName("Author")
        self.theme_description = QLabel(Theme.description)
        self.theme_description.setObjectName("ThemeDescription")
        self.theme_description.setWordWrap(True)

        self.import_theme_button = QPushButton(Traduction.get_trad("import_theme", "Import"))
        self.delete_theme_button = QPushButton(Traduction.get_trad("delete_theme", "Delete"))
        self.import_theme_button.clicked.connect(self.on_import_theme)
        self.delete_theme_button.clicked.connect(self.on_delete_theme)
        self._refresh_delete_button_state()

        authors_layout = QHBoxLayout()
        authors_layout.addWidget(self.theme_author)
        authors_layout.addWidget(self.theme_author_name)
        authors_layout.addStretch()

        information_layout = QVBoxLayout()
        information_layout.setContentsMargins(0, 5, 0, 0)
        information_layout.addWidget(self.theme_title)
        information_layout.addLayout(authors_layout)
        information_layout.addWidget(self.theme_description)
        information_layout.addStretch()

        combobox_layout = QHBoxLayout()
        combobox_layout.addStretch()
        combobox_layout.addWidget(self.theme_combo)

        manage_theme_layout = QHBoxLayout()
        manage_theme_layout.addStretch()
        manage_theme_layout.addWidget(self.import_theme_button)
        manage_theme_layout.addWidget(self.delete_theme_button)

        action_layout = QVBoxLayout()
        action_layout.addLayout(combobox_layout)
        action_layout.addStretch()
        action_layout.addLayout(manage_theme_layout)

        appearance_layout = QHBoxLayout()
        appearance_layout.addLayout(information_layout)
        appearance_layout.addStretch()
        appearance_layout.addLayout(action_layout)
        self.layout.addLayout(appearance_layout)

    def _build_language_section(self):
        self.language_title = self.make_section_title("language", "Language")
        self.layout.addWidget(self.language_title)

        self.lang_combo = QComboBox()
        for label, code in Traduction.get_languages():
            self.lang_combo.addItem(label, code)

        self.lang_combo.setCurrentIndex(self.lang_combo.findData(Config.lang))
        self.lang_combo.setPlaceholderText("English")
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
            row.setContentsMargins(0, 0, 2, 0)
            self.layout.addLayout(row)

    def _build_footer(self):
        self.layout.addStretch(1)
        self.close_button = QPushButton(Traduction.get_trad("close", "Close"))
        self.close_button.clicked.connect(self.accept)

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(self.close_button)
        footer.setContentsMargins(0, 0, 10, 10)
        self.root_layout.addLayout(footer)

    def _populate_theme_combo(self, imported):
        self.theme_combo.clear()
        themes_names = self.get_themes_names(imported)

        for i in range(len(themes_names[0])):
            self.theme_combo.addItem(themes_names[1][i], themes_names[0][i])
        if themes_names[2] != -1:
            self.theme_combo.insertSeparator(themes_names[2])

    def get_themes_names(self, imported):
        temp_list = []
        separator_index = -1
        themes = (Info.get_files_from_directory("resource_path", "themes/", ".yml"))

        for theme in themes:
            if "_" in theme:
                temp_list.append(theme)
                themes.remove(theme)
        separator_index = len(themes)
        if temp_list:
            themes = themes + temp_list

        temp_list = Info.get_files_from_directory("config_path", "themes/", ".yml")
        if temp_list:
            for theme in temp_list:
                if theme not in themes:
                    themes.append(theme)
        name = Theme.get_properties("name", Config.lang.upper())
        names = Theme.get_theme_names(themes, Config.lang.upper(), imported)
        return themes, names, separator_index

    def _refresh_delete_button_state(self):
        current = self.theme_combo.currentData()

    def on_theme_changed(self):
        theme = self.theme_combo.currentData()
        if not theme or theme == Config.theme:
            return

        Config.theme = theme
        ConfigManager.save_config()
        self._apply_theme()
        Logger.LogMessage(f"SETTINGS: Theme changed to: {theme}")

    def on_import_theme(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Theme", "", "YAML Theme Files (*.yml)")
        if not path:
            return

        file_name = path.rsplit("/", 1)[1]
        config_theme_path = Info.get_config_path()+"/themes/"
        Info.ensure_dir_exists(config_theme_path)
        temp_list = Info.get_files_from_directory("config_path", "themes/", ".yml")

        for temp_file in temp_list:
            if file_name == temp_file:
                text = f"Theme with file name {temp_file} exists.\n\n How do you want to approach?\n"
                question = Modal.create("import_theme_exist", self, text)
                if question == "ok":
                    index = 0
                    terms = temp_file.rsplit("_")
                    while index < len(temp_list):
                        if terms[0]+f"({index})_"+terms[1] in temp_list:
                            index += 1
                        else:
                            break
                    try:
                        shutil.copy(path, config_theme_path+terms[0]+f"({index})_"+terms[1])
                    except Exception as exception:
                        if Config.DEBUG:
                            Debug.Error(f"Failed to copy theme file: {exception}")
                    self._populate_theme_combo(True)
                    self.theme_combo.setCurrentIndex(self.theme_combo.count() - 1)
                    return

                elif question == "yes":
                    try:
                        shutil.copy(path, config_theme_path+file_name)
                    except Exception as exception:
                        if Config.DEBUG:
                            Debug.Error(f"Failed to copy theme file: {exception}")
                return

        try:
            shutil.copy(path, config_theme_path+file_name)
        except Exception as exception:
            if Config.DEBUG:
                Debug.Error(f"Failed to copy theme file: {exception}")

    def on_delete_theme(self):
        themes = (Info.get_files_from_directory("config_path", "themes/", ".yml"))
        name = self.theme_combo.currentData()

        for theme in themes:
            if name == theme:
                text = f"Theme {name} will be deleted.\n\n Are you sure?\n"
                if Modal.create("delete_theme", self, text) == "yes":
                    os.remove(Info.get_config_path()+"/themes/"+theme)
                    self._populate_theme_combo(True)
                    self.theme_combo.setCurrentIndex(0)
                return

        if "_" in name:
            text = f"Theme {name} not found in config directory.\n"
        else:
            text = f"Standard theme {name} cannot be deleted.\n"
        Modal.create("delete_theme_not_exist", self, text)

    def on_lang_changed(self):
        lang = self.lang_combo.currentData()
        if not lang or lang == Config.lang:
            return
        Config.lang = lang
        Traduction.set_translate_model(lang)
        ConfigManager.save_config()
        self.traduction_changed.emit()
        self.refresh_ui_texts()
        Logger.LogMessage(f"Language changed to: {lang}")

    def on_shebang_changed(self):
        new_value = self.shebang_input.text().strip()
        if not new_value:
            self.shebang_input.setText(Config.CUSTOM_SHEBANG)
            return
        if new_value == Config.CUSTOM_SHEBANG:
            return

        if Modal.create("shebang_change", self) == "yes":
            Config.CUSTOM_SHEBANG = new_value
            ConfigManager.save_config()
            Logger.LogMessage(f"Custom shebang changed to: {new_value}")
            return
        self.shebang_input.setText(Config.CUSTOM_SHEBANG)
        Logger.LogWarning(f"Custom shebang change cancelled.")

    def refresh_ui_texts(self):
        self.setWindowTitle(Traduction.get_trad("settings", "Settings"))

        self.appearance_title.setText(Traduction.get_trad("appearance", "Appearance"))
        self.theme_author_name.setText(Theme.author)
        self.language_title.setText(Traduction.get_trad("language", "Language"))
        self.advanced_title.setText(Traduction.get_trad("advanced", "Advanced"))
        self.theme_title.setText(Traduction.get_trad("theme", "Theme"))
        self.language_label.setText(Traduction.get_trad("language", "Language"))
        self.shebang_label.setText(Traduction.get_trad("custom_shebang", "Custom Shebang"))
        self.close_button.setText(Traduction.get_trad("close", "Close"))
        self.import_theme_button.setText(Traduction.get_trad("import_theme", "Import…"))
        self.delete_theme_button.setText(Traduction.get_trad("delete_theme", "Delete"))
        if Theme.author.count(" ") > 0:
            self.theme_author.setText(Traduction.get_trad("authors", "Authors"))
        else:
            self.theme_author.setText(Traduction.get_trad("author", "Author"))

        for attr, key, fallback in [
            ("debug", "debug", "Debug mode"),
            ("using_tty", "using_tty", "Use TTY"),
            ("sync_nodes_and_gen", "sync_nodes_and_gen", "Sync Nodes and Generation"),
            ("auto_save", "auto_save", "Auto Save"),
        ]:
            label = getattr(self, f"{attr}_label", None)
            if label:
                label.setText(Traduction.get_trad(key, fallback))

        themes_names = self.get_themes_names(False)
        for i in range(len(themes_names[0])):
            idx = self.theme_combo.findData(themes_names[0][i])
            self.theme_combo.setItemText(idx, themes_names[1][i])

        if self.parent():
            self.parent().toolbar.apply_ui_texts()

    def _apply_theme(self):
        self.scroll_area.setStyleSheet(scroll_style())
        self.theme_combo.setStyleSheet(combobox_style())
        self.lang_combo.setStyleSheet(combobox_style())
        self.import_theme_button.setStyleSheet(pushbutton_style())
        self.delete_theme_button.setStyleSheet(pushbutton_style())
        self.close_button.setStyleSheet(pushbutton_style())
        self.shebang_input.setStyleSheet(lineedit_style())

        for widget in self.layout.parent().children():
            if isinstance(widget, QLabel):
                widget.setStyleSheet(label_style())
            elif isinstance(widget, QFrame):
                widget.setStyleSheet(separator_style())
        for widget in self.root_layout.parent().children():
            if isinstance(widget, QFrame) and not isinstance(widget, QScrollArea):
                widget.setStyleSheet(separator_style())

        self.setStyleSheet(f"background: {Theme.get_color("SETTINGS-BACKGROUND")}")
        self.content_widget.setStyleSheet("QWidget#SettingsContent { background: transparent; }")

        if self.parent():
            self.parent().graph_view._apply_theme()
            self.parent().toolbar._apply_theme()
            self.parent().refresh_ui_colors()

        self.theme_description.setText(Theme.description)
        if Theme.author.count(" ") > 0:
            self.theme_author.setText(Traduction.get_trad("authors", "Authors"))
        else:
            self.theme_author.setText(Traduction.get_trad("author", "Author"))
        self.theme_author_name.setText(Theme.author)


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
        painter.setBrush(QColor(Theme.get_color("SETTINGS-SETTING_ENABLED")) if self._checked else QColor(Theme.get_color("SETTINGS-SETTING_DISABLED")))
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


def label_style() -> str:
    return f"""
            QLabel {{
                color: {Theme.get_color("SETTINGS-LABEL_TEXT")};
            }}
            QLabel#SectionTitle {{
                font-weight: bold;
                font-size: 16px;
                color: {Theme.get_color("SETTINGS-TITELLABEL_TEXT")};
            }}
            QLabel#ThemeDescription {{
                font-style: italic;
                color: {Theme.get_color("SETTINGS-DESCRIPTIONLABEL_TEXT")};
            }}
            QLabel#Author {{
                color: {Theme.get_color("SETTINGS-AUTHORLABEL_TEXT")};
            }}
        """

def scroll_style() -> str:
    return f"""
            QScrollArea#SettingsScrollArea {{
                background: {Theme.get_color("SCROLL_AREA")};
                border: none;
            }}
            QScrollArea#SettingsScrollArea > QWidget > QWidget {{
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

def combobox_style() -> str:
    return f"""
            QComboBox {{
                color: {Theme.get_color("SETTINGS-COMBOBOX_TEXT")};
                border: 1px solid {Theme.get_color("SETTINGS-COMBOBOX_BORDER")};
                border-radius: 5px;
                padding: 3px 0px 3px 5px;
                background: {Theme.get_color("SETTINGS-COMBOBOX_BACKGROUND")};
                combobox-popup: 0;
            }}
            QComboBox:focus,
            QComboBox:selected,
            QComboBox:hover {{
                border-color: {Theme.get_color("SETTINGS-COMBOBOX_BORDER_HOVER")};
                background: {Theme.get_color("SETTINGS-COMBOBOX_BACKGROUND_HOVER")};
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {Theme.get_color("SETTINGS-COMBOBOX_BORDER")};
                border-radius: 5px;
                background: {Theme.get_color("SETTINGS-COMBOBOX_MAIN_BACKGROUND")};
                padding: 5px;
            }}
            QComboBox QAbstractItemView:item:focus {{
                background: {Theme.get_color("SETTINGS-COMBOBOX_SELECTION")};
                border-radius: 5px;
            }}
            QComboBox::separator {{
                background: {Theme.get_color("SETTINGS-COMBOBOX_SEPARATOR")};
            }}
        """

def pushbutton_style() -> str:
    return f"""
            QPushButton {{
                color: {Theme.get_color("SETTINGS-PUSHBUTTON_TEXT")};
                border: 1px solid {Theme.get_color("SETTINGS-PUSHBUTTON_BORDER")};
                border-radius: 5px;
                min-width: 60px;
                padding: 3px 5px;
                background: {Theme.get_color("SETTINGS-PUSHBUTTON_BACKGROUND")};
            }}
            QPushButton:focus,
            QPushButton:selected,
            QPushButton:hover {{
                border-color: {Theme.get_color("SETTINGS-PUSHBUTTON_BORDER_HOVER")};
                background: {Theme.get_color("SETTINGS-PUSHBUTTON_BACKGROUND_HOVER")};
                outline: none;
            }}
        """

def lineedit_style() -> str:
    return f"""
            QLineEdit {{
                color: {Theme.get_color("SETTINGS-LINEEDIT_TEXT")};
                border: 1px solid {Theme.get_color("SETTINGS-LINEEDIT_BORDER")};
                border-radius: 5px;
                padding: 3px 5px;
                background: {Theme.get_color("SETTINGS-LINEEDIT_BACKGROUND")};
                selection-background-color: {Theme.get_color("SETTINGS-LINEEDIT_SELECTION")};
                selection-color: {Theme.get_color("SETTINGS-LINEEDIT_SELECTION_TEXT")};
            }}
            QLineEdit:focus,
            QLineEdit:selected,
            QLineEdit:hover {{
                border-color: {Theme.get_color("SETTINGS-LINEEDIT_BORDER_HOVER")};
            }}
        """

def separator_style() -> str:
    return f"""
            QFrame[frameShape="4"] {{
                border: none;
                max-height: 1px;
                background: {Theme.get_color("SETTINGS-SEPARATOR")};
            }}
        """
