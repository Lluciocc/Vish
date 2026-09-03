# main.py
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

import os
import subprocess
import sys
import time

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMainWindow,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.ansi_to_html import ansi_to_html
from core.bash_emitter import BashEmitter
from core.config import Config, ConfigManager
from core.debug import Debug, Info
from core.graph import Graph
from core.highlights import BashHighlighter
from core.icons import Icon
from core.logger import Logger
from core.projects import ProjectManager
from core.serializer import Serializer
from core.traduction import Traduction
from nodes.flow_nodes import StartNode
from nodes.registry import NODE_REGISTRY
from themes.theme_manager import Theme
from ui.about.about import AboutDialog
from ui.comment_box import COMMENT_Z_BASE, CommentBoxItem
from ui.graph_view import GraphView
from ui.keyboard_shortcuts import KeyboardShortcutsDialog
from ui.main_style import Style
from ui.modal import Modal
from ui.property_panel import PropertyPanel
from ui.settings import SettingsDialog
from ui.toolbar import Toolbar
from ui.welcome import WelcomeScreen

IS_WINDOWS = sys.platform == "win32"
if not IS_WINDOWS:
    import pty


class NodeFactory:
    @staticmethod
    def create_node(node_type: str):
        entry = NODE_REGISTRY.get(node_type)
        return entry["class"]() if entry else None


class VisualBashEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Bash Editor")
        self.resize(1400, 900)
        self.setMinimumSize(360, 294)

        self.graph = Graph()
        self.node_factory = NodeFactory()
        self.project_manager = ProjectManager()

        self.setup_ui()
        self.create_initial_graph()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(Style.toolpanels_style())
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        self.toolbar = Toolbar(self)
        main_layout.addLayout(self.toolbar)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(12)

        self.graph_view = GraphView(self.graph, self)
        self.graph_view.setStyleSheet(Style.apply_viewport_style())
        self.splitter.addWidget(self.graph_view)

        self.property_panel = PropertyPanel(graph_view=self.graph_view)
        self.splitter.addWidget(self.property_panel)

        self.output_splitter = QSplitter(Qt.Vertical)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumWidth(300)
        self.run_output_text = QTextEdit()
        self.run_output_text.setReadOnly(True)
        self.run_output_text.setVisible(False)
        self.run_output_text.setMinimumHeight(150)
        self.run_output_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.run_output_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.run_output_text.setLineWrapMode(QTextEdit.NoWrap)

        self.output_splitter.addWidget(self.output_text)
        self.output_splitter.addWidget(self.run_output_text)
        self.output_splitter.setSizes([300, 0])
        self.output_splitter.setStyleSheet(Style.apply_bash_textedit_style())

        self.splitter.addWidget(self.output_splitter)

        self.output_text.setStyleSheet(f"color: {Theme.get_color('MAIN-BASH_TEXT')}")
        self.bash_highlighter = BashHighlighter(self.output_text.document())

        self.splitter.setSizes([900, 300, 400])
        main_layout.addWidget(self.splitter)

        self._connect_signals()

    def resizeEvent(self, event):
        self.toolbar.resize_buttons(event.size().width())
        if Info.get_device_type() == "phone":
            if self.splitter.orientation() is self.splitter.orientation().Horizontal:
                if event.size().width() < event.size().height():
                    self.splitter.setOrientation(Qt.Vertical)
            else:
                if event.size().width() > event.size().height():
                    self.splitter.setOrientation(Qt.Horizontal)

        super().resizeEvent(event)

    def create_initial_graph(self):
        start_node = StartNode()
        start_node.x = 100
        start_node.y = 100
        self.graph.add_node(start_node)
        self.graph_view.add_node_item(start_node)
        self.property_panel.set_node(start_node)

    def add_node(self, node_type: str):
        node = self.node_factory.create_node(node_type)
        if node:
            node.x = 400
            node.y = 300
            self.graph.add_node(node)
            self.graph_view.add_node_item(node)

    def generate_bash(self):
        if not self.graph.nodes:
            Debug.Warn(
                Traduction.get_trad(
                    "warn_generating_empty_graph", "Generating an empty graph."
                )
            )
        emitter = BashEmitter(self.graph)
        bash_script = emitter.emit()
        self.output_text.setPlainText(bash_script)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.traduction_changed.connect(self.graph_view.update_language)
        dialog.exec()

    def open_about(self):
        AboutDialog(self).exec()

    def toggle_full_screen(self):
        if self.windowState() & Qt.WindowState.WindowFullScreen:
            self.setWindowState(Qt.WindowState.WindowNoState)
            self.toolbar.fullscreen_action.setIcon(
                Icon.load_icon("menu_app", "fullscreen")
            )
            if "fullscreen_button" in self.toolbar.toolbar:
                self.toolbar.fullscreen_button.setIcon(
                    Icon.load_icon("menu_app", "fullscreen")
                )
        else:
            self.setWindowState(Qt.WindowState.WindowFullScreen)
            self.toolbar.fullscreen_action.setIcon(
                Icon.load_icon("menu_app", "windowmode")
            )
            if "fullscreen_button" in self.toolbar.toolbar:
                self.toolbar.fullscreen_button.setIcon(
                    Icon.load_icon("menu_app", "windowmode")
                )

    def open_keyboard_shortcuts(self):
        KeyboardShortcutsDialog(self).exec()

    def open_welcome_screen(self):
        welcome = WelcomeScreen(self, self.project_manager)
        if welcome.exec() == QDialog.Accepted:
            self.load_current_project()
        else:
            Debug.Log(
                Traduction.get_trad(
                    "no_project_loaded",
                    "No project loaded. You can create or open a project from the welcome screen.",
                )
            )

    def save_graph(self, msg=True):
        if not self.graph.nodes:
            Debug.Error(
                Traduction.get_trad(
                    "error_cannot_save_empty_graph", "Cannot save an empty graph."
                )
            )
            return

        if not self.project_manager.get_project_path():
            if msg:  # Notice that without this, this func is called every frame when having an AUTO_SAVE=True, might need to fix this in the future
                Debug.Error("No project loaded.")
            return

        file_path = self.project_manager.get_graph_path()

        json_data = Serializer.serialize(self.graph, self.graph_view)

        with open(file_path, "w") as f:
            f.write(json_data)

        if msg:
            Debug.Log("Project saved.")

    def load_graph(self):
        projects_path = os.path.dirname(
            os.path.dirname(self.project_manager.get_graph_path())
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            Traduction.get_trad("file_dialog_open", "Load Graph"),
            f"{projects_path}/graph.json",
            "JSON Files (*.json)",
        )

        if not file_path:
            Debug.Error(
                Traduction.get_trad("error_no_file_selected", "No file selected.")
            )
            return

        with open(file_path, "r") as f:
            json_data = f.read()

        self._load_graph_data(json_data)

        Debug.Log(
            Traduction.get_trad(
                "graph_loaded_successfully",
                f"Graph loaded successfully from {file_path} with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.",
                file_path=file_path,
                node_count=len(self.graph.nodes),
                edge_count=len(self.graph.edges),
            )
        )

        if Config.SYNC_NODES_AND_GEN:
            self.generate_bash()

    def load_current_project(self):
        graph_path = self.project_manager.get_graph_path()

        if not graph_path.exists():
            return

        with open(graph_path, "r") as f:
            json_data = f.read()

        self._load_graph_data(json_data)

        if Config.DEBUG:
            Logger.LogMessage(
                f"Loaded project from {graph_path} with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges."
            )

        if Config.SYNC_NODES_AND_GEN:
            self.generate_bash()

    def _load_graph_data(self, json_data):
        try:
            self.graph, comments, viewport = Serializer.deserialize(
                json_data, self.node_factory
            )
        except ValueError as e:
            text = f"Project contains unknown node type: '{e.args[0][1]}'\nPlease check if a newer version of this tool is available."
            Modal.create("unknown_nodes", self, text)
            raise

        splitter = self.graph_view.parent()
        old_view = self.graph_view

        self.graph_view = GraphView(self.graph, self)
        splitter.insertWidget(0, self.graph_view)

        old_view.setParent(None)
        old_view.deleteLater()

        self.property_panel.graph_view = self.graph_view
        self.clear_property_panel()

        for node in self.graph.nodes.values():
            self.graph_view.add_node_item(node)

        for edge in self.graph.edges.values():
            self.graph_view.graph_scene.add_core_edge(edge, self.graph_view.node_items)

        comment_count = len(comments)
        for index, comment in enumerate(comments):
            if "z" not in comment:
                comment = dict(comment)
                comment["z"] = COMMENT_Z_BASE + comment_count - index - 1
            self.load_comment(comment)

        comment_items = [
            item
            for item in self.graph_view.scene().items()
            if isinstance(item, CommentBoxItem)
        ]
        if comment_items:
            comment_items[0].normalize_comment_z_order()

        # Reset z counter based on loaded nodes to ensure new nodes are on top
        max_z = max((node.z for node in self.graph.nodes.values()), default=0)
        self.graph_view.graph_scene._z_counter = max_z + 1

        # Restore viewport after loading graph to ensure it's centered on the correct position
        if viewport:
            if Config.DEBUG:
                Logger.LogMessage(
                    f"Restoring viewport position: x={viewport.get('x', 0)}, y={viewport.get('y', 0)}, zoom={viewport.get('zoom', 1.0)}"
                )
            QTimer.singleShot(0, lambda: self._restore_viewport(viewport))

        self._connect_signals()
        splitter.setSizes([900, 300, 400])

    def _restore_viewport(self, viewport):
        center = QPointF(viewport.get("x", 0), viewport.get("y", 0))
        self.graph_view.set_zoom(viewport.get("zoom", 1.0))
        self.graph_view.centerOn(center)
        self.graph_view.setStyleSheet(Style.apply_viewport_style())
        self.graph_view.setFocus()

    def load_comment(self, comment):
        box = CommentBoxItem(
            rect=QRectF(0, 0, comment["w"], comment["h"]),
            title=comment["title"],
            body_text=comment.get("body", ""),
        )
        box.setPos(comment["x"], comment["y"])
        box.setZValue(comment.get("z", box.zValue()))
        box.set_locked(comment.get("locked", False))
        box._accent_index = comment.get("color_index", 0)
        box.set_title_size_index(comment.get("size_index", 2))
        box.move_children = comment.get("move_children", True)
        box.setRect(QRectF(0, 0, comment["w"], comment["h"]))
        self.graph_view.scene().addItem(box)

    def clear_property_panel(self):
        self.property_panel.clear()

    def auto_save(self):
        if Config.AUTO_SAVE:
            self.save_graph(msg=False)

    def _connect_signals(self):
        self.graph_view.graph_scene.graph_changed.connect(self.generate_bash)
        self.graph_view.graph_scene.graph_changed.connect(self.auto_save)
        self.graph_view.graph_scene.node_selected.connect(self.property_panel.set_node)
        self.graph_view.graph_scene.auto_save_triggered.connect(self.auto_save)
        self.graph_view.clear_property_panel_request.connect(self.clear_property_panel)

    def run_pty(self, script_path: str) -> str:
        master_fd, slave_fd = pty.openpty()

        proc = subprocess.Popen(
            ["bash", "-i", script_path],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            text=False,
        )

        os.close(slave_fd)

        output = b""
        while True:
            try:
                chunk = os.read(master_fd, 1024)
                if not chunk:
                    break
                output += chunk
            except OSError:
                break

        proc.wait()
        os.close(master_fd)

        output = output.decode(errors="replace")

        filtered = []
        for line in (
            output.splitlines()
        ):  # NOTE: i have to filter some lines because bash -i outputs them
            if (
                "cannot set terminal process group" in line
                or "no job control in this shell" in line
            ):
                continue
            filtered.append(line)

        return "\n".join(filtered)

    def find_bash(self):
        if not IS_WINDOWS:
            return "bash"

        possible_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        import shutil

        bash_in_path = shutil.which("bash")
        if bash_in_path:
            return bash_in_path

        return None

    def run_no_pty(self, script_path: str) -> str:
        bash_cmd = self.find_bash()

        if not bash_cmd:
            return (
                "\x1b[1;31mError:\x1b[0m\n"
                "No Bash executable found.\nInstall Git Bash or enable WSL."
            )

        result = subprocess.run([bash_cmd, script_path], capture_output=True, text=True)

        if result.stderr:
            return f"\x1b[1;31mError:\x1b[0m\n{result.stderr}"

        return result.stdout

    def run_bash(self):
        if Info.get_os() == "Windows":
            Debug.Warn(
                Traduction.get_trad(
                    "running_windows", "It is not possible to run scripts on Windows."
                )
            )
            return
        self.set_run_output_visible(True)
        bash_script = self.output_text.toPlainText()
        self.run_output_text.clear()
        if (
            not bash_script.strip() or len(bash_script) == 49
        ):  # 49 is length of the header
            Debug.Warn(
                Traduction.get_trad(
                    "no_bash_script", "No bash script found to run the graph."
                )
            )
            return

        temp_script_path = f"temp_script_{int(time.time())}.sh"
        with open(temp_script_path, "w") as f:
            f.write(bash_script)

        os.chmod(temp_script_path, 0o755)

        Debug.Log(
            Traduction.get_trad(
                "running_generated_bash_script", "Running generated bash script..."
            )
        )

        try:
            if Config.USING_TTY:
                output = self.run_pty(temp_script_path)
            else:
                output = self.run_no_pty(temp_script_path)

            self.run_output_text.setVisible(True)
            self.output_splitter.setSizes([200, 150])

            self.run_output_text.setHtml(ansi_to_html(output))

        except Exception as e:
            self.run_output_text.setVisible(True)
            self.run_output_text.setPlainText(str(e))

        finally:
            os.remove(temp_script_path)

    def set_run_output_visible(self, visible: bool):
        self.run_output_text.setVisible(visible)

    def toggle_run_output(self):
        visible = self.run_output_text.isVisible()
        self.run_output_text.setVisible(not visible)

        if visible:
            self.output_splitter.setSizes([1, 0])
        else:
            self.output_splitter.setSizes([200, 150])

    def refresh_ui_colors(self):
        self.graph_view.setStyleSheet(Style.apply_viewport_style())
        self.output_splitter.setStyleSheet(Style.apply_bash_textedit_style())
        self.central_widget.setStyleSheet(Style.toolpanels_style())
        self.output_text.setStyleSheet(f"color: {Theme.get_color('MAIN-BASH_TEXT')}")
        self.bash_highlighter = BashHighlighter(self.output_text.document())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Save):  # Ctrl+S
            self.save_graph()
        elif event.matches(QKeySequence.Open):  # Ctrl+O
            self.load_graph()
        elif (
            event.key() == Qt.Key_G and event.modifiers() & Qt.ControlModifier
        ):  # Ctrl+G
            self.generate_bash()
        elif (
            event.key() == Qt.Key_R and event.modifiers() & Qt.ControlModifier
        ):  # Ctrl+R
            self.run_bash()
        elif (
            event.key() == Qt.Key_W and event.modifiers() & Qt.ControlModifier
        ):  # Ctrl+W
            self.open_welcome_screen()
        elif event.key() == Qt.Key_F11:  # F11
            self.toggle_full_screen()
        elif event.key() == Qt.Key_F1:  # F1
            self.open_keyboard_shortcuts()
        elif event.key() == Qt.Key_F9:  # F9
            self.open_settings()
        elif event.key() == Qt.Key_Escape:  # Esc
            if self.windowState() & Qt.WindowState.WindowFullScreen:
                self.setWindowState(Qt.WindowState.WindowNoState)
        elif (
            event.key() == Qt.Key_L
            and event.modifiers() & Qt.ControlModifier
            and event.modifiers() & Qt.AltModifier
        ):  # Ctrl+Shift+L
            Debug.Warn("Log file saved with current logs.")
            Logger.save_logged_messages()

        super().keyPressEvent(event)


def main():
    ConfigManager.load_config()  # Load config before setting theme and language
    Traduction.set_translate_model(Config.lang)

    app = QApplication(sys.argv)

    app.setOrganizationName("Lluciocc")
    app.setApplicationName("Vish")
    icon_path = Info.resource_path("assets/icons/Vish.svg")
    app.setWindowIcon(QIcon(icon_path))
    editor = VisualBashEditor()
    app.setStyle("Fusion")

    Debug.init(editor)
    editor.show()

    editor.open_welcome_screen()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Logger.LogWarning("Application interrupted by user.")
    except Exception as e:
        Logger.LogError(f"Fatal error: {e}")
        Logger.save_logged_messages(str(e))
