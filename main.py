import sys
IS_WINDOWS = sys.platform == "win32"

if not IS_WINDOWS:
    import pty

import os
import sys
import subprocess
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QPushButton, QHBoxLayout, QTextEdit,
                               QSplitter, QFileDialog, QToolButton, QMenu, QDialog)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QKeySequence, QIcon
from core.graph import Graph
from core.bash_emitter import BashEmitter
from core.serializer import Serializer
from nodes.flow_nodes import StartNode, IfNode, ForNode
from nodes.command_nodes import RunCommandNode, EchoNode, ExitNode
from nodes.variable_nodes import SetVariableNode, GetVariableNode, FileExistsNode
from nodes.operation_nodes import Addition
from nodes.utils_node import ToString
from ui.comment_box import CommentBoxItem
from ui.graph_view import GraphView
from ui.property_panel import PropertyPanel
from ui.settings import SettingsDialog
from ui.menu_style import apply_btn_style, apply_menu_style, apply_icon_for_btn
from ui.about.about import AboutDialog
from ui.keyboard_shortcuts import KeyboardShortcutsDialog
from nodes.registry import NODE_REGISTRY
from core.highlights import BashHighlighter
from core.ansi_to_html import ansi_to_html
from core.config import Config, ConfigManager
from core.debug import Info, Debug
from core.traduction import Traduction
from core.projects import ProjectManager
from ui.welcome import WelcomeScreen
from theme.theme import Theme, set_dark_theme, set_purple_theme, set_white_theme

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
        
        self.graph = Graph()
        self.node_factory = NodeFactory()
        self.project_manager = ProjectManager()
        
        self.setup_ui()
        self.create_initial_graph()
    
    def setup_ui(self):
        if Config.theme == "dark":
            set_dark_theme()
        elif Config.theme == "purple":
            set_purple_theme()
        elif Config.theme == "white":
            set_white_theme()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        toolbar = QHBoxLayout()

        self.generate_btn = QPushButton(Traduction.get_trad("btn_generate_bash", "Generate Bash"))
        self.generate_btn.clicked.connect(self.generate_bash)
        apply_icon_for_btn(self.generate_btn, "generate")
        toolbar.addWidget(self.generate_btn)

        self.save_btn = QPushButton(Traduction.get_trad("btn_save", "Save"))
        apply_icon_for_btn(self.save_btn, "save")
        self.save_btn.clicked.connect(self.save_graph)
        toolbar.addWidget(self.save_btn)

        self.load_btn = QPushButton(Traduction.get_trad("btn_load", "Load"))
        self.load_btn.clicked.connect(self.load_graph)
        apply_icon_for_btn(self.load_btn, "load")
        toolbar.addWidget(self.load_btn)

        toolbar.addStretch()

        self.run_bash_btn = QPushButton(Traduction.get_trad("btn_run_bash", "Run Bash Script"))
        self.run_bash_btn.clicked.connect(self.run_bash)
        apply_icon_for_btn(self.run_bash_btn, "play")
        toolbar.addWidget(self.run_bash_btn)

        self.copy_btn = QPushButton(Traduction.get_trad("btn_copy_clipboard", "Copy to Clipboard"))
        apply_icon_for_btn(self.copy_btn, "clipboard")
        self.copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.output_text.toPlainText())
        )
        toolbar.addWidget(self.copy_btn)

        self.more_btn = QToolButton()
        self.more_btn.setText("⋮")
        self.more_btn.setPopupMode(QToolButton.InstantPopup)
        apply_btn_style(self.more_btn)


        self.more_menu = QMenu(self)
        apply_menu_style(self.more_menu)

        self.settings_action = self.more_menu.addAction(
            Traduction.get_trad("settings", "Settings")
        )
        self.settings_action.triggered.connect(self.open_settings)
        apply_icon_for_btn(self.settings_action, "settings")

        self.keyboard = self.more_menu.addAction(
            Traduction.get_trad("keyboard_shortcuts", "Keyboard Shortcuts")
        )
        self.keyboard.triggered.connect(self.open_keyboard_shortcuts)
        apply_icon_for_btn(self.keyboard, "keyboard")

        self.full_screenfs = self.more_menu.addAction(
            Traduction.get_trad("full_screen", "Full Screen")
        )
        self.full_screenfs.triggered.connect(self.full_screen_action)
        apply_icon_for_btn(self.full_screenfs, "fullscreen")
        self.about_action = self.more_menu.addAction(
            Traduction.get_trad("about", "About")
        )
        self.about_action.triggered.connect(self.open_about)
        apply_icon_for_btn(self.about_action, "about")


        self.more_btn.setMenu(self.more_menu)
        toolbar.addWidget(self.more_btn)

        main_layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)

        self.graph_view = GraphView(self.graph, self)
        splitter.addWidget(self.graph_view)
        
        self.property_panel = PropertyPanel()
        splitter.addWidget(self.property_panel)

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

        splitter.addWidget(self.output_splitter)

        self.bash_highlighter = BashHighlighter(self.output_text.document())

        splitter.setSizes([900, 300, 400])
        main_layout.addWidget(splitter)

        self._connect_signals()


    def create_initial_graph(self):
        start_node = StartNode()
        start_node.x = 100
        start_node.y = 100
        self.graph.add_node(start_node)
        self.graph_view.add_node_item(start_node)
    
    def add_node(self, node_type: str):
        node = self.node_factory.create_node(node_type)
        if node:
            node.x = 400
            node.y = 300
            self.graph.add_node(node)
            self.graph_view.add_node_item(node)
    
    def generate_bash(self):
        if not self.graph.nodes:
            Debug.Warn(Traduction.get_trad("warn_generating_empty_graph", "Generating an empty graph."))
        print(f"EDGES: {len(self.graph.edges)}")
        emitter = BashEmitter(self.graph)
        bash_script = emitter.emit()
        self.output_text.setPlainText(bash_script)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.traduction_changed.connect(self.graph_view.rebuild_graph)
        dialog.exec()

    def open_about(self):
        AboutDialog(self).exec()

    def full_screen_action(self):
        if self.windowState() & Qt.WindowState.WindowFullScreen:
            self.setWindowState(Qt.WindowState.WindowNoState)
        else:
            self.setWindowState(Qt.WindowState.WindowFullScreen)

    def open_keyboard_shortcuts(self):
        KeyboardShortcutsDialog(self).exec()
        
    def save_graph(self, msg=True):
        if not self.graph.nodes:
            Debug.Error(Traduction.get_trad("error_cannot_save_empty_graph", "Cannot save an empty graph."))
            return

        if not self.project_manager.get_project_path():
            Debug.Error("No project loaded.")
            return

        file_path = self.project_manager.get_graph_path()

        json_data = Serializer.serialize(self.graph, self.graph_view)

        with open(file_path, 'w') as f:
            f.write(json_data)

        if msg:
            Debug.Log("Project saved.")

    
    def load_graph(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Graph", "", "JSON Files (*.json)"
        )
        if not file_path:
            Debug.Error(Traduction.get_trad("error_no_file_selected", "No file selected."))
            return

        with open(file_path, "r") as f:
            json_data = f.read()

        self.graph, comments = Serializer.deserialize(json_data, self.node_factory)


        splitter = self.graph_view.parent()
        old_view = self.graph_view

        self.graph_view = GraphView(self.graph, self)
        splitter.insertWidget(0, self.graph_view)

        old_view.setParent(None)
        old_view.deleteLater()

        for node in self.graph.nodes.values():
            self.graph_view.add_node_item(node)

        for edge in self.graph.edges.values():
            self.graph_view.graph_scene.add_core_edge(edge, self.graph_view.node_items)
        
        for c in comments:
            box = CommentBoxItem(
                rect=QRectF(0, 0, c["w"], c["h"]),
                title=c["title"]
            )
            box.setPos(c["x"], c["y"])
            box.setBrush(QColor(*c["color"]))
            box.set_locked(c.get("locked", False))
            self.graph_view.scene().addItem(box)

        self._connect_signals()
        splitter.setSizes([900, 300, 400])

        Debug.Log(Traduction.get_trad("graph_loaded_successfully", f"Graph loaded successfully from {file_path} with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.", file_path=file_path, node_count=len(self.graph.nodes), edge_count=len(self.graph.edges)))

    def load_current_project(self):
        graph_path = self.project_manager.get_graph_path()

        if not graph_path.exists():
            return

        with open(graph_path, "r") as f:
            json_data = f.read()

        self.graph, comments = Serializer.deserialize(json_data, self.node_factory)

        splitter = self.graph_view.parent()
        old_view = self.graph_view

        self.graph_view = GraphView(self.graph, self)
        splitter.insertWidget(0, self.graph_view)

        old_view.setParent(None)
        old_view.deleteLater()

        self._connect_signals()

        for node in self.graph.nodes.values():
            self.graph_view.add_node_item(node)

        for edge in self.graph.edges.values():
            self.graph_view.graph_scene.add_core_edge(edge, self.graph_view.node_items)

        splitter.setSizes([900, 300, 400])

    def auto_save(self):
        if Config.AUTO_SAVE:
            self.save_graph(msg=False)

    def _connect_signals(self):
        self.graph_view.graph_scene.graph_changed.connect(self.generate_bash)
        self.graph_view.graph_scene.graph_changed.connect(self.auto_save)
        self.graph_view.graph_scene.node_selected.connect(self.property_panel.set_node)

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
        for line in output.splitlines(): # NOTE: i have to filter some lines because bash -i outputs them
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
            r"C:\Program Files (x86)\Git\bin\bash.exe"
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

        result = subprocess.run(
            [bash_cmd, script_path],
            capture_output=True,
            text=True
        )

        if result.stderr:
            return f"\x1b[1;31mError:\x1b[0m\n{result.stderr}"

        return result.stdout

    
    def run_bash(self):
        if Info.get_os() == "Windows":
            Debug.Warn(Traduction.get_trad("running_windows", "It is not possible to run scripts on Windows."))
            return
        self.set_run_output_visible(True)
        bash_script = self.output_text.toPlainText()
        self.run_output_text.clear()
        if not bash_script.strip() or len(bash_script) == 49: # 49 is length of the header
            Debug.Warn(Traduction.get_trad("no_bash_script", "No bash script found to run the graph."))
            return

        temp_script_path = f"temp_script_{int(time.time())}.sh"
        with open(temp_script_path, "w") as f:
            f.write(bash_script)

        os.chmod(temp_script_path, 0o755)

        Debug.Log(Traduction.get_trad("running_generated_bash_script", "Running generated bash script..."))

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

    def refresh_ui_texts(self):
        self.generate_btn.setText(Traduction.get_trad("btn_generate_bash", "Generate Bash"))
        self.save_btn.setText(Traduction.get_trad("btn_save", "Save"))
        self.load_btn.setText(Traduction.get_trad("btn_load", "Load"))
        self.run_bash_btn.setText(Traduction.get_trad("btn_run_bash", "Run Bash Script"))
        self.copy_btn.setText(Traduction.get_trad("btn_copy_clipboard", "Copy to Clipboard"))

        self.more_btn.setToolTip(Traduction.get_trad("more_options", "More options"))
        self.settings_action.setText(Traduction.get_trad("settings", "Settings"))
        self.about_action.setText(Traduction.get_trad("about", "About"))
        self.keyboard.setText(Traduction.get_trad("keyboard_shortcuts", "Keyboard Shortcuts"))

        apply_icon_for_btn(self.settings_action, "settings")
        apply_icon_for_btn(self.about_action, "about")
        apply_icon_for_btn(self.keyboard, "keyboard")
        apply_icon_for_btn(self.generate_btn, "generate")
        apply_icon_for_btn(self.load_btn, "load")
        apply_icon_for_btn(self.run_bash_btn, "play")
        apply_icon_for_btn(self.copy_btn, "clipboard")
        apply_icon_for_btn(self.save_btn, "save")
        apply_icon_for_btn(self.full_screenfs, "fullscreen")

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Save): # Ctrl+S
            self.save_graph()
        elif event.matches(QKeySequence.Open): # Ctrl+O
            self.load_graph()
        elif event.key() == Qt.Key_G and event.modifiers() & Qt.ControlModifier: # Ctrl+G
            self.generate_bash()
        elif event.key() == Qt.Key_R and event.modifiers() & Qt.ControlModifier: # Ctrl+R
            self.run_bash()
        super().keyPressEvent(event)

def main():
    ConfigManager.load_config() # Load config before setting theme and language
    Traduction.set_translate_model(Config.lang)

    app = QApplication(sys.argv)
    app.setOrganizationName("Lluciocc")
    app.setApplicationName("Vish")
    app.setWindowIcon(QIcon(Info.resource_path("assets/icons/icon.png")))
    editor = VisualBashEditor()

    Debug.init(editor)
    editor.show()

    welcome = WelcomeScreen(editor, editor.project_manager)
    if welcome.exec() == QDialog.Accepted:
        editor.load_current_project()
    elif welcome.result() == QDialog.Rejected:
        Debug.Log(Traduction.get_trad("no_project_loaded", "No project loaded. You can create or open a project from the welcome screen."))

    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Application interrupted by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
