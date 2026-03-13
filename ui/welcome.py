from pathlib import Path
from datetime import datetime, timezone
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton,
    QListWidget, QLabel, QInputDialog,
    QFileDialog, QMessageBox, QListWidgetItem,
    QWidget, QHBoxLayout, QAbstractItemView,
    QLineEdit
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QKeySequence, QColor, QShortcut
from ui.menu_style import apply_btn_style
from core.traduction import Traduction
from core.projects import ProjectManager
from theme.theme import Theme


def _format_last_modified(iso: str | None) -> str:
    if not iso:
        return Traduction.get_trad("never_modified", "Never saved")
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%d %b %Y  %H:%M")
    except Exception:
        return ""


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

        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 8, 6)
        layout.setSpacing(10)

        text_col = QWidget()
        text_col.setStyleSheet("background: transparent;")
        self._text_layout = QVBoxLayout(text_col)
        self._text_layout.setContentsMargins(0, 0, 0, 0)
        self._text_layout.setSpacing(2)

        self.name_label = ClickableLabel(name)
        self.name_label.setStyleSheet(
            f"color: {Theme.TEXT}; font-weight: 600; font-size: 10pt; background: transparent;"
        )
        self.name_label.clicked.connect(self.start_rename)
        self._text_layout.addWidget(self.name_label)

        date_str = _format_last_modified(last_modified)
        if date_str:
            self.date_label = QLabel(date_str)
            self.date_label.setStyleSheet("color: #777; font-size: 8pt; background: transparent;")
            self._text_layout.addWidget(self.date_label)
        else:
            self.date_label = None

        self.name_editor = QLineEdit(name)
        self.name_editor.setStyleSheet(f"""
            QLineEdit {{
                color: {Theme.TEXT};
                background: {Theme.PANEL};
                border: 1px solid {Theme.BUTTON};
                border-radius: 4px;
                font-weight: 600;
                font-size: 10pt;
                padding: 1px 4px;
            }}
        """)
        self.name_editor.setVisible(False)
        self.name_editor.returnPressed.connect(self._commit_rename)
        self.name_editor.editingFinished.connect(self._commit_rename)
        self.name_editor.textChanged.connect(self._resize_rename)
        self.name_editor.installEventFilter(self)
        self._text_layout.insertWidget(0, self.name_editor)

        layout.addWidget(text_col, stretch=1)

        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(26, 26)
        delete_btn.setToolTip(Traduction.get_trad("remove_recent", "Remove from recents"))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666;
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(192, 57, 43, 0.85);
                color: white;
            }
            QPushButton:pressed {
                background-color: rgba(150, 40, 30, 0.95);
                color: white;
            }
        """)
        delete_btn.clicked.connect(lambda: on_delete(path_str))
        layout.addWidget(delete_btn)

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


class WelcomeScreen(QDialog):
    def __init__(self, parent, project_manager: ProjectManager):
        super().__init__(parent)

        self.project_manager = project_manager
        self._renaming_active = False

        self.setWindowTitle("  ")
        self.setModal(True)
        self.setMinimumSize(360, 294)
        self.setFixedSize(620, 480)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.TEXT};
                background: transparent;
            }}
            QListWidget {{
                background-color: {Theme.PANEL};
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 10px;
                padding: 6px;
                color: {Theme.TEXT};
                outline: none;
            }}
            QListWidget::item {{
                padding: 0px;
                border-radius: 7px;
                margin: 2px 0px;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.BUTTON};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {Theme.BUTTON_HOVER};
            }}
            QScrollBar:vertical {{ width: 0px; }}
            QScrollBar:horizontal {{ height: 0px; }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(40, 32, 40, 32)

        title = QLabel(Traduction.get_trad("welcome_title", "Welcome"))
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Theme.TEXT}; background: transparent; font-size: 18pt;")
        main_layout.addWidget(title)

        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: rgba(255,255,255,0.08);")
        main_layout.addWidget(separator)

        recent_label = QLabel(Traduction.get_trad("welcome_recent_projects", "Recent Projects"))
        recent_label.setStyleSheet(f"color: {Theme.TEXT}; font-weight: bold; font-size: 9pt; letter-spacing: 1px;")
        main_layout.addWidget(recent_label)

        self.recent_list = QListWidget()
        self.recent_list.setFocusPolicy(Qt.StrongFocus)
        self.recent_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.recent_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recent_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recent_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.recent_list.itemDoubleClicked.connect(self._on_item_double_click)
        main_layout.addWidget(self.recent_list)

        self.populate_recent_projects()

        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(16)
        button_layout.setContentsMargins(0, 4, 0, 0)

        self.new_btn = QPushButton(Traduction.get_trad("welcome_new_project", "New Project"))
        apply_btn_style(self.new_btn)
        self.new_btn.clicked.connect(self.create_project)
        self.new_btn.setMinimumHeight(38)

        self.open_btn = QPushButton(Traduction.get_trad("welcome_open_project", "Open Project"))
        apply_btn_style(self.open_btn)
        self.open_btn.clicked.connect(self.open_project)
        self.open_btn.setMinimumHeight(38)

        hover_style = f"QPushButton:hover {{ background-color: {Theme.BUTTON_HOVER}; }}"
        self.open_btn.setStyleSheet(self.open_btn.styleSheet() + hover_style)
        self.new_btn.setStyleSheet(self.new_btn.styleSheet() + hover_style)

        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.open_btn)
        main_layout.addWidget(button_container)

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
            self.new_btn.setFocus()

    def _handle_enter(self):
        focused = self.focusWidget()

        if isinstance(focused, QLineEdit):
            focused.editingFinished.emit()
            return

        if self.recent_list.count() > 0 and self.recent_list.currentItem() is not None:
            self.open_recent(self.recent_list.currentItem())
            return

        if focused is self.new_btn:
            self.new_btn.click()
        elif focused is self.open_btn:
            self.open_btn.click()

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
            placeholder.setForeground(QColor("#555"))
            self.recent_list.addItem(placeholder)

    def _rename_project(self, path_str: str, new_name: str):
        project_file = Path(path_str) / "project.json"
        if not project_file.exists():
            return
        try:
            data = json.loads(project_file.read_text())
            data["name"] = new_name
            project_file.write_text(json.dumps(data, indent=4))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _remove_recent(self, path_str: str):
        reply = QMessageBox.question(
            self,
            Traduction.get_trad("remove_recent", "Remove from recents"),
            Traduction.get_trad(
                "remove_recent_question",
                "Do you want to remove this project from the recent list?"
            ),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
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
            self.new_btn.setFocus()

        self.project_manager.remove_project(Path(path_str))

    def create_project(self):
        name, ok = QInputDialog.getText(
            self,
            Traduction.get_trad("new_project_name", "Project Name"),
            Traduction.get_trad("new_project_enter_name", "Enter project name:")
        )

        if not ok or not name.strip():
            return

        base_dir = Path(self.project_manager.config_dir) / "projects"
        project_dir = base_dir / name.strip()

        try:
            self.project_manager.create_project(project_dir, name.strip())
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

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
            QMessageBox.critical(self, "Error", str(e))

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
            QMessageBox.critical(self, "Error", str(e))