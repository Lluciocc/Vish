from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal

class NodePalette(QWidget):
    node_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Node")
        self.resize(300, 400)
        
        layout = QVBoxLayout(self)
        self.setWindowFlags(Qt.Popup)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search nodes...")
        self.search_input.textChanged.connect(self.filter_nodes)
        layout.addWidget(self.search_input)
        
        self.node_list = QListWidget()
        self.node_list.itemDoubleClicked.connect(self.on_node_selected)
        layout.addWidget(self.node_list)
        
        self.nodes = [
            ("Start", "start"),
            ("Run Command", "run_command"),
            ("Echo", "echo"),
            ("Exit", "exit"),
            ("If", "if"),
            ("For Loop", "for"),
            ("Set Variable", "set_variable"),
            ("Get Variable", "get_variable"),
            ("File Exists", "file_exists"),
        ]
        
        self.populate_nodes()
    
    def populate_nodes(self):
        self.node_list.clear()
        for name, node_type in self.nodes:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, node_type)
            self.node_list.addItem(item)
    
    def filter_nodes(self, text):
        for i in range(self.node_list.count()):
            item = self.node_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def on_node_selected(self, item):
        node_type = item.data(Qt.UserRole)
        self.node_selected.emit(node_type)
        self.close()
    
    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
