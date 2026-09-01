# toolbar.py
#
# Copyright 2026 Ick
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

from core.config import Config
from core.icons import Icon
from core.traduction import Traduction
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMenu, QPushButton, QToolButton
from themes.theme_manager import Theme


class Toolbar(QHBoxLayout):
    def __init__(self, editor):
        super().__init__()

        self.editor = editor
        self.setup_buttons()
        # icon name + type (also used as config identifier) | setup_button | traduction | signal
        self.TOOLS = {
            "generate_button": [self.generate_button, ("button_generate_bash", "Generate Bash"), self.editor.generate_bash],
            "save_button": [self.save_button, ("button_save", "Save"), self.editor.save_graph],
            "load_button": [self.load_button, ("button_load", "Load"), self.editor.load_graph],
            "run_bash_button": [self.run_bash_button, ("button_run_bash", "Run Bash Script"), self.editor.run_bash],
            "clipboard_button": [self.copy_button, ("button_copy_clipboard", "Copy to Clipboard"), self.copy_to_clipboard()],
            "hamburger_menu_button": [self.hamburger_button, ("more_options", "More options")],
            "settings_button": [self.settings_button, ("settings", "Settings"), self.editor.open_settings],
            "settings_action": [self.settings_action, ("settings", "Settings"), self.editor.open_settings],
            "keyboard_button": [self.keyboard_button, ("keyboard_shortcuts", "Keyboard Shortcuts"), self.editor.open_keyboard_shortcuts],
            "keyboard_action": [self.keyboard_action, ("keyboard_shortcuts", "Keyboard Shortcuts"), self.editor.open_keyboard_shortcuts],
            "fullscreen_button": [self.fullscreen_button, ("full_screen", "Full Screen"), self.editor.toggle_full_screen],
            "fullscreen_action": [self.fullscreen_action, ("full_screen", "Full Screen"), self.editor.toggle_full_screen],
            "about_button": [self.about_button, ("about", "About"), self.editor.open_about],
            "about_action": [self.about_action, ("about", "About"), self.editor.open_about],
        }
        self.setup_signals()
        self.apply_ui_texts()
        self._apply_theme()

        self.toolbar = Config.TOOLBAR
        self.min_width = 0
        for button in self.toolbar:
            if button == "stretch":
                self.addStretch()
            elif button in self.TOOLS:
                self.min_width += self.TOOLS[button][0].sizeHint().width() + 8
                self.addWidget(self.TOOLS[button][0])

    def setup_buttons(self):
        self.generate_button = QPushButton()
        self.save_button = QPushButton()
        self.load_button = QPushButton()
        self.run_bash_button = QPushButton()
        self.copy_button = QPushButton()
        self.settings_button = QPushButton()
        self.keyboard_button = QPushButton()
        self.fullscreen_button = QPushButton()
        self.about_button = QPushButton()

        self.hamburger_button = QToolButton()
        self.hamburger_button.setText("☰")
        self.hamburger_button.setPopupMode(QToolButton.InstantPopup)
        self.more_menu = QMenu(self.editor)

        self.settings_action = self.more_menu.addAction("")
        self.keyboard_action = self.more_menu.addAction("")
        self.fullscreen_action = self.more_menu.addAction("")
        self.about_action = self.more_menu.addAction("")

        self.hamburger_button.setMenu(self.more_menu)

    def setup_signals(self):
        for items in self.TOOLS:
            if isinstance(self.TOOLS[items][0], QPushButton):
                self.TOOLS[items][0].clicked.connect(self.TOOLS[items][2])
            elif isinstance(self.TOOLS[items][0], QAction):
                self.TOOLS[items][0].triggered.connect(self.TOOLS[items][2])

    def resize_buttons(self, width):
        if self.min_width > width:
            self.apply_ui_texts(False)
        else:
            self.apply_ui_texts()

    def copy_to_clipboard(self):
        return lambda: QApplication.clipboard().setText(self.editor.output_text.toPlainText())

    def apply_ui_texts(self, text=True):
        for items in self.TOOLS:
            if isinstance(self.TOOLS[items][0], QToolButton):
                self.TOOLS[items][0].setToolTip(Traduction.get_trad(*self.TOOLS[items][1]))
            elif isinstance(self.TOOLS[items][0], QPushButton):
                if text == True:
                    self.TOOLS[items][0].setText(Traduction.get_trad(*self.TOOLS[items][1]))
                    self.TOOLS[items][0].setToolTip("")
                else:
                    self.TOOLS[items][0].setText("")
                    self.TOOLS[items][0].setToolTip(Traduction.get_trad(*self.TOOLS[items][1]))
            else:
                self.TOOLS[items][0].setText(Traduction.get_trad(*self.TOOLS[items][1]))

    def _apply_theme(self):
        for button in self.TOOLS:
            if not isinstance(self.TOOLS[button][0], QToolButton):
                self.TOOLS[button][0].setIcon(Icon.load_icon("menu_app", button.rsplit("_", 1)[0]))
                if isinstance(self.TOOLS[button][0], QPushButton):
                    self.TOOLS[button][0].setStyleSheet(pushbutton_style())
            elif isinstance(self.TOOLS[button][0], QToolButton):
                self.TOOLS[button][0].setStyleSheet(toolbutton_style())

        self.more_menu.setStyleSheet(apply_menu_style())


def apply_menu_style() -> str:
    return f"""
        QMenu {{
            background: {Theme.get_color("TOOLBAR-MENU_BACKGROUND")};
            color: {Theme.get_color("TOOLBAR-MENU_TEXT")};
            border-radius: 12px;
            padding: 8px;
            border: 1px solid {Theme.get_color("TOOLBAR-MENU_BORDER")};
            font-size: 14px;
        }}
        QMenu::icon {{
            padding: 0px 0px 0px 15px;
        }}
        QMenu::item {{
            padding: 10px 5px 10px 15px;
            border-radius: 8px;
            min-width: 150px;
        }}
        QMenu::item:selected {{
            background: {Theme.get_color("TOOLBAR-MENU_ITEM_SELECTION")};
        }}
    """

def toolbutton_style() -> str:
    return f"""
            QToolButton {{
                color: {Theme.get_color("TOOLBAR-TOOLBUTTON_TEXT")};
                border: 1px solid {Theme.get_color("TOOLBAR-TOOLBUTTON_BORDER")};
                font-size: 15px;
                padding: 4px 8px;
                border-radius: 5px;
            }}
            QToolButton:hover {{
                background: {Theme.get_color("TOOLBAR-TOOLBUTTON_BACKGROUND_HOVER")};
                border: 1px solid {Theme.get_color("TOOLBAR-TOOLBUTTON_BORDER_HOVER")};
            }}
            QToolButton:pressed {{
                background: {Theme.get_color("TOOLBAR-TOOLBUTTON_BACKGROUND_PRESSED")};
            }}
            QToolButton::menu-indicator {{
                image: none;
            }}
        """

def pushbutton_style() -> str:
    return f"""
            QPushButton {{
                color: {Theme.get_color("TOOLBAR-PUSHBUTTON_TEXT")};
                border: 1px solid {Theme.get_color("TOOLBAR-PUSHBUTTON_BORDER")};
                border-radius: 5px;
                min-width: 26px;
                min-height: 26px;
                padding: 3px 5px;
                background: {Theme.get_color("TOOLBAR-PUSHBUTTON_BACKGROUND")};
                outline: none;
            }}
            QPushButton:hover {{
                border-color: {Theme.get_color("TOOLBAR-PUSHBUTTON_BORDER_HOVER")};
                background: {Theme.get_color("TOOLBAR-PUSHBUTTON_BACKGROUND_HOVER")};
            }}
            QPushButton:pressed {{
                background: {Theme.get_color("TOOLBAR-PUSHBUTTON_BACKGROUND_PRESSED")};
            }}
        """
