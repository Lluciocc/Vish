import os
import sys
import subprocess
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QPushButton, QHBoxLayout, QTextEdit,
                               QSplitter, QFileDialog, QComboBox)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor
from core.graph import Graph
from core.bash_emitter import BashEmitter
from core.serializer import Serializer
from core.debug import Debug
from nodes.flow_nodes import StartNode, IfNode, ForNode
from nodes.command_nodes import RunCommandNode, EchoNode, ExitNode
from nodes.variable_nodes import SetVariableNode, GetVariableNode, FileExistsNode
from nodes.operation_nodes import Addition
from nodes.utils_node import ToString
from ui.comment_box import CommentBoxItem
from ui.graph_view import GraphView
from ui.property_panel import PropertyPanel
from theme.theme import set_dark_theme, set_purple_theme, set_white_theme
from nodes.registry import NODE_REGISTRY
from core.highlights import BashHighlighter

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
        
        self.setup_ui()
        self.create_initial_graph()
    
    def setup_ui(self):
        set_dark_theme()
        #set_purple_theme()
        #set_white_theme()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        toolbar = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Bash")
        generate_btn.clicked.connect(self.generate_bash)
        toolbar.addWidget(generate_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_graph)
        toolbar.addWidget(save_btn)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_graph)
        toolbar.addWidget(load_btn)

        set_theme_btn = QComboBox()
        set_theme_btn.addItems(["Dark", "Purple", "White"])
        set_theme_btn.currentTextChanged.connect(self.set_theme)
        set_theme_btn.setFixedHeight(generate_btn.sizeHint().height())
        toolbar.addWidget(set_theme_btn)

        toolbar.addStretch()
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

        self.run_bash_btn = QPushButton("Run Bash Script")
        self.run_bash_btn.clicked.connect(self.run_bash)
        toolbar.addWidget(self.run_bash_btn)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.output_text.toPlainText()))
        toolbar.addWidget(self.copy_btn)

        self.run_output_text = QTextEdit()
        self.run_output_text.setReadOnly(True)
        self.run_output_text.setVisible(False)
        self.run_output_text.setMinimumHeight(150)

        self.output_splitter.addWidget(self.output_text)
        self.output_splitter.addWidget(self.run_output_text)
        self.output_splitter.setSizes([300, 0])

        splitter.addWidget(self.output_splitter)
        self.bash_highlighter = BashHighlighter(self.output_text.document())

        splitter.setSizes([900, 300, 400])
        main_layout.addWidget(splitter)

        self.graph_view.graph_scene.node_selected.connect(
            self.property_panel.set_node
        )

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
            Debug.Warn("Generating graph from an empty graph.")
        print(f"EDGES: {len(self.graph.edges)}")
        emitter = BashEmitter(self.graph)
        bash_script = emitter.emit()
        self.output_text.setPlainText(bash_script)
    
    def save_graph(self):
        if not self.graph.nodes:
            Debug.Warn("Cannot save an empty graph.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Graph", "", "JSON Files (*.json)"
        )
        if file_path:
            json_data = Serializer.serialize(self.graph, self.graph_view)
            with open(file_path, 'w') as f:
                f.write(json_data)
            Debug.Log(f"Graph saved to {file_path} with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")
    
    def load_graph(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Graph", "", "JSON Files (*.json)"
        )
        if not file_path:
            Debug.Error("No file selected for loading graph.")
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

        self.graph_view.graph_scene.node_selected.connect(
            self.property_panel.set_node
        )
        splitter.setSizes([900, 300, 400])

        Debug.Log(f"Graph loaded from {file_path} with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")

    def set_theme(self, theme_name: str):
        if theme_name == "Dark":
            set_dark_theme()
        elif theme_name == "Purple":
            set_purple_theme()
        elif theme_name == "White":
            set_white_theme()

        self.graph_view.apply_theme()

    def run_bash(self):
        self.set_run_output_visible(True)
        bash_script = self.output_text.toPlainText()
        self.run_output_text.clear()
        if not bash_script.strip():
            Debug.Warn("No bash script to run.")
            return

        temp_script_path = f"temp_script_{int(time.time())}.sh"
        with open(temp_script_path, "w") as f:
            f.write(bash_script)

        os.chmod(temp_script_path, 0o755)

        Debug.Log(f"Running generated bash script...")

        try:
            result = subprocess.run(
                ["bash", temp_script_path],
                capture_output=True,
                text=True
            )
            output = result.stdout
            error = result.stderr

            self.run_output_text.setVisible(True)
            self.output_splitter.setSizes([200, 150])
            self.run_output_text.setPlainText(f"{output} \n{f'Error: \n{error}' if error else ''}")

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

def main():
    app = QApplication(sys.argv)
    editor = VisualBashEditor()
    Debug.init(editor)
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()