# modal.py
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
from core.logger import Logger
from core.traduction import Traduction
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QPushButton
from themes.theme_manager import Theme


# Supported dict entries:
#   ENTRY           DATA-TYPE               HINTS
#---------------------------------------------------------------
#   type            core.traduction         required
#   title           core.tratuction         recommented
#   message         core.traduction         recommented, not used with custom_message
#   buttons         array message-button    required and only used by type "question"
#   icon            message-icon            optional, not used by type "input"
#   default_button  message-button          optional, not used by type "input"
#   button_texts    array core.traduction   optional
#   button_icons    array core.icons        optional

MODALS = {
    "critical_exception": {
        "type": "info",
        "title": ("modal_title_error", "Error"),
        "icon": QMessageBox.Critical,
    },
    "remove_project": {
        "type": "question",
        "title": ("modal_title_remove_recent", "Remove from recents"),
        "message": ("modal_remove_recent_question", "Do you want to remove this project from the recent list?"),
        "icon": QMessageBox.Warning,
        "buttons": [QMessageBox.Yes, QMessageBox.No],
        "default_button": QMessageBox.No,
    },
    "create_project": {
        "type": "input",
        "title": ("modal_title_new_project", "Project Name"),
        "message": ("new_project_enter_name", "Enter project name:"),
    },
    "import_theme_exist": {
        "type": "question",
        "title": ("modal_title_import_theme_exist", "Theme is already existing"),
        "icon": QMessageBox.Question,
        "buttons": [QMessageBox.Ok, QMessageBox.Yes, QMessageBox.Cancel],
        "default_button": QMessageBox.Cancel,
        "button_texts": [("modal_rename_file", "Rename File"), ("modal_overwrite_file", "Overwrite File")],
        "button_icons": [],                         #TODO 2 entries
    },
    "delete_theme": {
        "type": "question",
        "title": ("modal_title_delete_theme", "Delete Theme"),
        "icon": QMessageBox.Warning,
        "buttons": [QMessageBox.Yes, QMessageBox.No],
        "default_button": QMessageBox.No,
        "button_texts": [("modal_delete_file", "Delete File")],
        "button_icons": [],                         #TODO 1 entry
    },
    "delete_theme_not_exist": {
        "type": "info",
        "title": ("modal_title_delete_theme", "Delete Theme"),
        "icon": QMessageBox.Information,
    },
    "shebang_change": {
        "type": "question",
        "title": ("modal_title_shebang", "Changing Shebang"),
        "message": ("modal_shebang_question", "Changing the shebang may break script execution on some systems.\n\nAre you sure you know what you are doing?"),
        "icon": QMessageBox.Warning,
        "buttons": [QMessageBox.Yes, QMessageBox.No],
        "default_button": QMessageBox.No,
    },
    "unknown_nodes": {
        "type": "info",
        "title": ("modal_title_unknown_nodes", "Unknown Nodes"),
        "icon": QMessageBox.Critical,
    },
    "open_link": {
        "type": "question",
        "title": ("modal_title_open_link", "Open Web-Link"),
        "icon": QMessageBox.Question,
        "buttons": [QMessageBox.Ok, QMessageBox.Yes, QMessageBox.Cancel],
        "default_button": QMessageBox.Cancel,
        "button_texts": [("modal_copy_link", "Copy Link"), ("modal_open_link", "Open Link")],
        "button_icons": [],                         #TODO 2 entries
    }
}

BUTTONDEFAULT = {
    QMessageBox.Ok: {
        "text": ("modal_button_ok", "Okay"),
        "icon": ("None", ""),                       #TODO
    },
    QMessageBox.Yes: {
        "text": ("modal_button_yes", "Yes"),
        "icon": ("None", ""),                       #TODO
    },
    QMessageBox.No: {
        "text": ("modal_button_no", "No"),
        "icon": ("None", ""),                       #TODO
    },
    QMessageBox.Cancel: {
        "text": ("modal_button_cancel", "Cancel"),
        "icon": ("None", ""),                       #TODO
    }
}

def show_message(data, parent, custom_message):
    exit_code = CustomMessageBox(data, parent, custom_message).exec_()
    match exit_code:
        case 0:
            return "interrupt"
        case 1024:
            return "ok"
        case 16384:
            return "yes"
        case 65536:
            return "no"
        case 4194304:
            return "cancel"

def get_input(data, parent):
    input_box = CustomInputBox(data, parent)
    exit_code = input_box.exec_()
    if exit_code == 1:
        if input_box.textValue() == "interrupt":
            input_box.setTextValue("interrupt ")
        return input_box.textValue()
    return "interrupt"


class Modal:
    def create(requested_modal, parent=None, custom_message=None):
        data = MODALS[requested_modal]
        modal_type = data["type"]
        match modal_type:
            case "question":
                return show_message(data, parent, custom_message)
            case "info":
                return show_message(data, parent, custom_message)
            case "input":
                return get_input(data, parent)


class CustomMessageBox(QMessageBox):
    def __init__(self, data, parent, custom_message):
        super().__init__(parent)

        if "title" in data:
            self.setWindowTitle(Traduction.get_trad(*data["title"]))
        else:
            self.setWindowTitle("")

        if custom_message:
            self.setText(custom_message)
        elif "message" in data:
            self.setText(Traduction.get_trad(*data["message"]))
        else:
            self.setText("")

        if "icon" in data:
            self.setIcon(data["icon"])
        else:
            self.setIcon(QMessageBox.NoIcon)
        self.setStyleSheet(box_style())

        if data["type"] == "info":
            self.setStandardButtons(QMessageBox.Ok)
            button = self.button(QMessageBox.Ok)
            button.setText(Traduction.get_trad(*BUTTONDEFAULT[QMessageBox.Ok]["text"]))
            button.setIcon(Icon.load_icon(*BUTTONDEFAULT[QMessageBox.Ok]["icon"]))

            button.setStyleSheet(pushbutton_style())
            return

        if "buttons" in data:
            match len(data["buttons"]):
                case 1:
                    self.setStandardButtons(data["buttons"][0])
                case 2:
                    self.setStandardButtons(data["buttons"][0] | data["buttons"][1])
                case 3:
                    self.setStandardButtons(data["buttons"][0] | data["buttons"][1] | data["buttons"][2])
                case _:
                    if Config.DEBUG:
                        Logger.LogError("MODAL: Zero or more than four buttons not supported.")
                    return
        else:
            self.setStandardButtons(QMessageBox.Cancel)

        if "default_button" in data:
            self.setDefaultButton(data["default_button"])

        for index in range(len(data["buttons"])):
            button = self.button(data["buttons"][index])
            button.setText(Traduction.get_trad(*BUTTONDEFAULT[data["buttons"][index]]["text"]))
            button.setIcon(Icon.load_icon(*BUTTONDEFAULT[data["buttons"][index]]["icon"]))
            button.setStyleSheet(pushbutton_style())

            if "button_texts" in data:
                if len(data["button_texts"]) > index:
                    if data["button_texts"][index]:
                        button.setText(Traduction.get_trad(*data["button_texts"][index]))
            if "button_icons" in data:
                if len(data["button_icons"]) > index:
                    if data["button_icons"][index]:
                        button.setIcon(Icon.load_icon(data["button_icons"][index]))

    def closeEvent(self, event):
        event.accept()


class CustomInputBox(QInputDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        if "title" in data:
            self.setWindowTitle(Traduction.get_trad(*data["title"]))
        else:
            self.setWindowTitle("")

        if "message" in data:
            self.setLabelText(Traduction.get_trad(*data["message"]))
        else:
            self.setLabelText("")

        self.setCancelButtonText(Traduction.get_trad(*BUTTONDEFAULT[QMessageBox.Cancel]["text"]))
        self.setOkButtonText(Traduction.get_trad(*BUTTONDEFAULT[QMessageBox.Ok]["text"]))
        if "button_texts" in data:
            if len(data["button_texts"]) > 0:
                if data["button_texts"][0]:
                    self.setCancelButtonText(Traduction.get_trad(*data["button_texts"][0]))
            if len(data["button_texts"]) > 1:
                if data["button_texts"][1]:
                    self.setOkButtonText(Traduction.get_trad(data["button_texts"][1]))

        self.findChildren(QPushButton)[0].setIcon(Icon.load_icon(*BUTTONDEFAULT[QMessageBox.Ok]["icon"]))
        self.findChildren(QPushButton)[1].setIcon(Icon.load_icon(*BUTTONDEFAULT[QMessageBox.Cancel]["icon"]))
        if "button_icons" in data:
            if len(data["button_icons"]) > 0:
                if data["button_icons"][0]:
                    self.findChildren(QPushButton)[0].setIcon(Icon.load_icon(*data["button_icons"][0]))
            if len(data["button_icons"]) > 1:
                if data["button_icons"][1]:
                    self.findChildren(QPushButton)[1].setIcon(Icon.load_icon(*data["button_icons"][1]))

        self.setStyleSheet(box_style())
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(pushbutton_style())
        self.findChild(QLineEdit).setStyleSheet(lineedit_style())


def lineedit_style() -> str:
    return f"""
            QLineEdit {{
                border: 1px solid {Theme.get_color("MODAL-LINEEDIT_BORDER")};
                border-radius: 5px;
                padding: 3px 5px;
                color: {Theme.get_color("MODAL-LINEEDIT_TEXT")};
                background: {Theme.get_color("MODAL-LINEEDIT_BACKGROUND")};
                selection-background-color: {Theme.get_color("MODAL-LINEEDIT_SELECTION_BACKGROUND")};
                selection-color: {Theme.get_color("MODAL-LINEEDIT_SELECTION_TEXT")};
            }}
            QLineEdit:focus,
            QLineEdit:selected,
            QLineEdit:hover {{
                border-color: {Theme.get_color("MODAL-LINEEDIT_BORDER_HOVER")};
            }}
        """

def box_style() -> str:
    return f"""
                background: {Theme.get_color("MODAL-BACKGROUND")};
                color: {Theme.get_color("MODAL-TEXT")};
        """

def pushbutton_style() -> str:
    return f"""
            QPushButton {{
                background: {Theme.get_color("MODAL-PUSHBUTTON_BACKGROUND")};
                color: {Theme.get_color("MODAL-PUSHBUTTON_TEXT")};
                border: 1px solid {Theme.get_color("MODAL-PUSHBUTTON_BORDER")};
                font-size: 15px;
                border-radius: 5px;
                padding: 3px 5px;
            }}
            QPushButton:focus,
            QPushButton:selected,
            QPushButton:hover {{
                background: {Theme.get_color("MODAL-PUSHBUTTON_BACKGROUND_HOVER")};
                border: 1px solid {Theme.get_color("MODAL-PUSHBUTTON_BORDER_HOVER")};
                outline: none;
            }}
        """
