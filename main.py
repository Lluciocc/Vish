import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QPushButton, QHBoxLayout, QTextEdit,
                               QSplitter, QFileDialog)
from PySide6.QtCore import Qt
from core.graph import Graph
from core.bash_emitter import BashEmitter
from core.serializer import Serializer
from nodes.flow_nodes import StartNode, IfNode, ForNode
from nodes.command_nodes import RunCommandNode, EchoNode, ExitNode
from nodes.variable_nodes import SetVariableNode, GetVariableNode, FileExistsNode
from nodes.operation_nodes import Addition
from ui.graph_view import GraphView
from ui.palette import NodePalette
from ui.property_panel import PropertyPanel
from theme.theme import set_dark_theme, set_purple_theme, set_white_theme
from nodes.registry import NODE_REGISTRY

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

        add_node_btn = QPushButton("Add Node")
        add_node_btn.clicked.connect(self.show_node_palette)
        toolbar.addWidget(add_node_btn)
        
        generate_btn = QPushButton("Generate Bash")
        generate_btn.clicked.connect(self.generate_bash)
        toolbar.addWidget(generate_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_graph)
        toolbar.addWidget(save_btn)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_graph)
        toolbar.addWidget(load_btn)
        
        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)

        self.graph_view = GraphView(self.graph, self)
        splitter.addWidget(self.graph_view)

        self.property_panel = PropertyPanel()
        splitter.addWidget(self.property_panel)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumWidth(300)
        splitter.addWidget(self.output_text)

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
    
    def show_node_palette(self):
        palette = NodePalette(self)
        palette.node_selected.connect(self.add_node)
        palette.show()
    
    def add_node(self, node_type: str):
        node = self.node_factory.create_node(node_type)
        if node:
            node.x = 400
            node.y = 300
            self.graph.add_node(node)
            self.graph_view.add_node_item(node)
    
    def generate_bash(self):
        print(f"EDGES: {len(self.graph.edges)}")
        emitter = BashEmitter(self.graph)
        bash_script = emitter.emit()
        self.output_text.setPlainText(bash_script)
    
    def save_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Graph", "", "JSON Files (*.json)"
        )
        if file_path:
            json_data = Serializer.serialize(self.graph)
            with open(file_path, 'w') as f:
                f.write(json_data)
    
    def load_graph(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Graph", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        with open(file_path, "r") as f:
            json_data = f.read()

        self.graph = Serializer.deserialize(json_data, self.node_factory)

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

    def set_theme(self, theme_fn):
        theme_fn()
        self.graph_view.scene().update()


def main():
    app = QApplication(sys.argv)
    editor = VisualBashEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()