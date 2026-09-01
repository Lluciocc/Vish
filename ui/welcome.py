# welcome.py
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

from core.debug import Info
from core.projects import ProjectManager
from core.traduction import Traduction
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QKeySequence, QColor, QShortcut
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QFileDialog, QHBoxLayout,
                               QLabel, QLineEdit, QListWidget, QListWidgetItem,
                               QPushButton, QVBoxLayout, QWidget)
from themes.theme_manager import Theme
import json
from ui.modal import Modal

class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ProjectListItem(QWidget):
    def __init__(self, name: str, path_str: str, last_modified: str | None, on_delete, on_rename, parent=None):
        super().__init__(parent)
        self.path_str = path_str
        self._name = name
        self._on_rename = on_rename
        self._renaming = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 8, 6)
        layout.setSpacing(10)

        text_col = QWidget()
        text_col.setStyleSheet("background: transparent;")
        self._text_layout = QVBoxLayout(text_col)
        self._text_layout.setContentsMargins(0, 0, 0, 0)
        self._text_layout.setSpacing(2)

        self.name_label = ClickableLabel(name)
        self.name_label.clicked.connect(self.start_rename)
        self._text_layout.addWidget(self.name_label)

        date_str = _format_last_modified(last_modified)
        if date_str:
            self.date_label = QLabel(date_str)
            self._text_layout.addWidget(self.date_label)
        else:
            self.date_label = None

        self.name_editor = QLineEdit(name)
        self.name_editor.setVisible(False)
        self.name_editor.returnPressed.connect(self._commit_rename)
        self.name_editor.editingFinished.connect(self._commit_rename)
        self.name_editor.textChanged.connect(self._resize_rename)
        self.name_editor.installEventFilter(self)
        self._text_layout.insertWidget(0, self.name_editor)

        layout.addWidget(text_col, stretch=1)

        self.delete_button = QPushButton("✕")
        self.delete_button.setFixedSize(26, 26)
        self.delete_button.setToolTip(Traduction.get_trad("remove_recent", "Remove from recents"))
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(lambda: on_delete(path_str))
        layout.addWidget(self.delete_button)
        self._apply_theme()

    def start_rename(self):
        if self._renaming:
            return

        self._renaming = True
        self.name_editor.setText(self._name)
        self._resize_rename(self._name)
        self.name_label.setVisible(False)
        self.name_editor.setVisible(True)
        self.name_editor.selectAll()
        self.name_editor.setFocus()

    def _resize_rename(self, text):
        metrics = self.name_editor.fontMetrics()
        width = metrics.horizontalAdvance(text + " ") + 20
        width = max(60, min(width, 400))
        self.name_editor.setFixedWidth(width)

    def cancel_rename(self):
        if not self._renaming:
            return
        self._renaming = False
        self.name_editor.setVisible(False)
        self.name_label.setVisible(True)
        self.name_editor.setText(self._name)

    def _commit_rename(self):
        if not self._renaming:
            return

        self._renaming = False
        new_name = self.name_editor.text().strip()

        self.name_editor.setVisible(False)
        self.name_label.setVisible(True)

        if new_name and new_name != self._name:
            self._name = new_name
            self.name_label.setText(new_name)
            self._on_rename(self.path_str, new_name)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj is self.name_editor and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.cancel_rename()
                return True
        return super().eventFilter(obj, event)

    def _apply_theme(self):
        self.delete_button.setStyleSheet(pushbutton_delete_style())
        self.name_editor.setStyleSheet(lineedit_style())
        self.name_label.setStyleSheet(label_name_style())
        self.date_label.setStyleSheet(label_time_style())

        self.setStyleSheet(f"background: {Theme.get_color("WELCOME-TOOLTIP_BACKGROUND")}")


class WelcomeScreen(QDialog):
    def __init__(self, parent, project_manager: ProjectManager):
        super().__init__(parent)

        self.project_manager = project_manager
        self._renaming_active = False

        self.setWindowTitle("  ")
        self.setModal(True)
        self.setMinimumSize(360, 294)
        if Info.get_device_type() == "phone":
            self.showMaximized()
        else:
            self.setFixedSize(620, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(40, 24, 40, 32)

        self.title = QLabel(Traduction.get_trad("welcome_title", "Welcome") + f", {Info.get_user().capitalize()}")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title)

        self.separator = QWidget()
        self.separator.setFixedHeight(1)
        main_layout.addWidget(self.separator)

        self.recent_label = QLabel(Traduction.get_trad("welcome_recent_projects", "Recent Projects"))
        main_layout.addWidget(self.recent_label)

        self.recent_list = QListWidget()
        self.recent_list.setFocusPolicy(Qt.StrongFocus)
        self.recent_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.recent_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recent_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recent_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.recent_list.itemDoubleClicked.connect(self._on_item_double_click)
        main_layout.addWidget(self.recent_list)

        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(16)
        button_layout.setContentsMargins(0, 4, 0, 0)

        self.new_button = QPushButton(Traduction.get_trad("welcome_new_project", "New Project"))
        self.new_button.clicked.connect(self.create_project)
        self.new_button.setMinimumHeight(38)

        self.open_button = QPushButton(Traduction.get_trad("welcome_open_project", "Open Project"))
        self.open_button.clicked.connect(self.open_project)
        self.open_button.setMinimumHeight(38)

        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.open_button)
        main_layout.addWidget(button_container)

        self._apply_theme()
        self.populate_recent_projects()
        self._setup_keyboard_nav()

    def _setup_keyboard_nav(self):
        for key in (Qt.Key_Return, Qt.Key_Enter):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(self._handle_enter)

        rename_shortcut = QShortcut(QKeySequence(Qt.Key_F2), self)
        rename_shortcut.activated.connect(self._handle_rename)

        if self.recent_list.count() > 0:
            self.recent_list.setCurrentRow(0)
            self.recent_list.setFocus()
        else:
            self.new_button.setFocus()

    def _handle_enter(self):
        focused = self.focusWidget()

        if isinstance(focused, QLineEdit):
            focused.editingFinished.emit()
            return

        if self.recent_list.count() > 0 and self.recent_list.currentItem() is not None:
            self.open_recent(self.recent_list.currentItem())
            return

        if focused is self.new_button:
            self.new_button.click()
        elif focused is self.open_button:
            self.open_button.click()

    def _handle_rename(self):
        item = self.recent_list.currentItem()
        if item is None or item.flags() == Qt.NoItemFlags:
            return

        widget = self._get_widget(item)
        if widget is None:
            return

        widget.start_rename()

    def _get_widget(self, item: QListWidgetItem) -> ProjectListItem | None:
        return self.recent_list.itemWidget(item)

    def _on_item_single_click(self, item: QListWidgetItem):
        widget = self._get_widget(item)
        if widget is None:
            return
        if getattr(widget, "_renaming", False):
            return

    def _on_item_double_click(self, item: QListWidgetItem):
        self.open_recent(item)

    def populate_recent_projects(self):
        self.recent_list.clear()

        recents = self.project_manager.get_recent_projects()

        for path_str in recents:
            path = Path(path_str)
            project_file = path / "project.json"
            project_name = path.name
            last_modified = None

            if project_file.exists():
                try:
                    data = json.loads(project_file.read_text())
                    project_name = data.get("name", path.name)
                    last_modified = data.get("last_modified")
                except Exception:
                    pass

            item = QListWidgetItem()
            item.setData(Qt.UserRole, path_str)
            item.setSizeHint(QSize(0, 54))

            widget = ProjectListItem(
                name=project_name,
                path_str=path_str,
                last_modified=last_modified,
                on_delete=self._remove_recent,
                on_rename=self._rename_project,
            )

            self.recent_list.addItem(item)
            self.recent_list.setItemWidget(item, widget)

        if self.recent_list.count() == 0:
            placeholder = QListWidgetItem(
                Traduction.get_trad("no_recent_projects", "No recent projects")
            )
            placeholder.setFlags(Qt.NoItemFlags)
            self.recent_list.addItem(placeholder)

    def _rename_project(self, path_str: str, new_name: str):
        try:
            self.project_manager.rename_project(Path(path_str), new_name)
            self.populate_recent_projects()

        except Exception as e:
            Modal.create("critical_exception", self, str(e))

    def _remove_recent(self, path_str: str):
        if Modal.create("remove_project", self) != "yes":
            return

        recents = self.project_manager.get_recent_projects()
        if path_str in recents:
            recents.remove(path_str)
            self.project_manager.recents_file.write_text(
                json.dumps(recents, indent=4)
            )
        self.populate_recent_projects()

        if self.recent_list.count() > 0 and self.recent_list.item(0).flags() != Qt.NoItemFlags:
            self.recent_list.setCurrentRow(0)
            self.recent_list.setFocus()
        else:
            self.new_button.setFocus()

        self.project_manager.remove_project(Path(path_str))

    def create_project(self):
        name = Modal.create("create_project", self)
        if not name.strip() or name == "interrupt":
            return

        base_dir = Path(self.project_manager.config_dir) / "projects"
        project_dir = base_dir / name.strip()

        try:
            self.project_manager.create_project(project_dir, name.strip())
            self.accept()
        except Exception as e:
            Modal.create("critical_exception", self, str(e))

    def open_project(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            Traduction.get_trad("select_project_folder", "Select Project Folder")
        )

        if not directory:
            return

        try:
            self.project_manager.load_project(Path(directory))
            self.accept()
        except Exception as e:
            Modal.create("critical_exception", self, str(e))

    def open_recent(self, item):
        if item is None or item.flags() == Qt.NoItemFlags:
            return

        widget = self._get_widget(item)
        if widget and getattr(widget, "_renaming", False):
            return

        path = item.data(Qt.UserRole)

        try:
            self.project_manager.load_project(Path(path))
            self.accept()
        except Exception as e:
            Modal.create("critical_exception", self, str(e))

    def _apply_theme(self):
        self.recent_label.setStyleSheet(label_recent_style())
        self.title.setStyleSheet(label_title_style())
        self.recent_list.setStyleSheet(listwidget_style())
        self.open_button.setStyleSheet(pushbutton_style())
        self.new_button.setStyleSheet(pushbutton_style())

        self.separator.setStyleSheet(f"background: {Theme.get_color("WELCOME-SEPARATOR")}")
        self.setStyleSheet(f"background-color: {Theme.get_color("WELCOME-BACKGROUND")}")


def _format_last_modified(iso: str | None) -> str:
    if not iso:
        return Traduction.get_trad("never_modified", "Never saved")
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%d %b %Y  %H:%M")
    except Exception:
        return ""

def lineedit_style() -> str:
    return f"""
            QLineEdit {{
                border: 1px solid {Theme.get_color("WELCOME-LINEEDIT_BORDER")};
                border-radius: 5px;
                padding: 3px 5px;
                background: {Theme.get_color("WELCOME-LINEEDIT_BACKGROUND")};
                selection-background-color: {Theme.get_color("WELCOME-LINEEDIT_SELECTION")};
                selection-color: {Theme.get_color("WELCOME-LINEEDIT_SELECTION_TEXT")};
                color: {Theme.get_color("WELCOME-LINEEDIT_TEXT")};
            }}
            QLineEdit:focus,
            QLineEdit:selected,
            QLineEdit:hover {{
                border-color: {Theme.get_color("WELCOME-LINEEDIT_BORDER_HOVER")};
            }}
        """

def pushbutton_delete_style() -> str:
    return f"""
            QPushButton {{
                background: {Theme.get_color("WELCOME-DELETEBUTTON_BACKGROUND")};;
                color: {Theme.get_color("WELCOME-DELETEBUTTON_TEXT")};
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 0;
            }}
            QPushButton:focus,
            QPushButton:selected,
            QPushButton:hover {{
                background: {Theme.get_color("WELCOME-DELETEBUTTON_BACKGROUND_HOVER")};
                color: {Theme.get_color("WELCOME-DELETEBUTTON_TEXT_HOVER")};
                outline: none;
            }}
            QPushButton:pressed {{
                background: {Theme.get_color("WELCOME-DELETEBUTTON_BACKGROUND_PRESSED")};
                color: {Theme.get_color("WELCOME-DELETEBUTTON_TEXT_PRESSED")};
            }}
        """

def label_name_style() -> str:
    return f"""
            color: {Theme.get_color("WELCOME-NAMELABEL_TEXT")};
            font-weight: 600;
            font-size: 11pt;
            background: {Theme.get_color("WELCOME-NAMELABEL_BACKGROUND")};
        """

def label_time_style() -> str:
    return f"""
            color: {Theme.get_color("WELCOME-DATELABEL_TEXT")};
            font-size: 8pt;
            font-style: italic;
            background: {Theme.get_color("WELCOME-DATELABEL_BACKGROUND")};
        """

def label_recent_style() -> str:
    return f"""
            color: {Theme.get_color("WELCOME-SUBLABEL_TEXT")};
            background: {Theme.get_color("WELCOME-SUBLABEL_BACKGROUND")};
            font-weight: bold;
            font-size: 11pt;
            letter-spacing: 1px;
        """

def label_title_style() -> str:
    return f"""
            color: {Theme.get_color("WELCOME-TITLELABEL_TEXT")};
            background: {Theme.get_color("WELCOME-TITLELABEL_BACKGROUND")};
            font-size: 18pt;
        """

def listwidget_style() -> str:
    return f"""
            QListWidget {{
                background: {Theme.get_color("WELCOME-LISTWIDGET_BACKGROUND")};
                border: 1px solid {Theme.get_color("WELCOME-LISTWIDGET_BORDER")};
                border-radius: 10px;
                padding: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 0px;
                border-radius: 7px;
                margin: 2px 0px;
            }}
            QListWidget::item:selected {{
                background: {Theme.get_color("WELCOME-LISTWIDGET_BUTTON_SELECTION")};
            }}
            QListWidget::item:hover:!selected {{
                background: {Theme.get_color("WELCOME-LISTWIDGET_BUTTON_HOVER")};
            }}
        """

def pushbutton_style() -> str:
    return f"""
            QPushButton {{
                color: {Theme.get_color("WELCOME-PUSHBUTTON_TEXT")};
                border: 1px solid {Theme.get_color("WELCOME-PUSHBUTTON_BORDER")};
                font-size: 15px;
                border-radius: 5px;
                min-width: 60px;
                padding: 3px 5px;
                outline: none;
            }}
            QPushButton:hover {{
                background: {Theme.get_color("WELCOME-PUSHBUTTON_BACKGROUND_HOVER")};
                border: 1px solid {Theme.get_color("WELCOME-PUSHBUTTON_BORDER_HOVER")};
            }}
            QPushButton:pressed {{
                background: {Theme.get_color("WELCOME-PUSHBUTTON_BACKGROUND_PRESSED")};
            }}
        """
