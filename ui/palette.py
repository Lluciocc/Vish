from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from nodes.registry import NODE_REGISTRY


class NodePalette(QWidget):
    node_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Node")
        self.resize(320, 420)
        self.setWindowFlags(Qt.Popup)

        layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search nodes...")
        self.search_input.textChanged.connect(self.filter_nodes)
        layout.addWidget(self.search_input)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_item_activated)
        layout.addWidget(self.tree)

        self._node_chosen = False
        self.populate_tree()

    def populate_tree(self):
        self.tree.clear()

        categories = {}

        for node_type, meta in NODE_REGISTRY.items():
            cat = meta["category"]
            categories.setdefault(cat, []).append(
                (meta["label"], node_type)
            )

        for category in sorted(categories.keys()):
            cat_item = QTreeWidgetItem([category])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)
            cat_item.setExpanded(True)

            for label, node_type in sorted(categories[category]):
                item = QTreeWidgetItem([label])
                item.setData(0, Qt.UserRole, node_type)
                item.setToolTip(0, meta["description"])
                cat_item.addChild(item)

            self.tree.addTopLevelItem(cat_item)

    def filter_nodes(self, text):
        text = text.lower()

        for i in range(self.tree.topLevelItemCount()):
            category = self.tree.topLevelItem(i)
            visible_category = False

            for j in range(category.childCount()):
                item = category.child(j)
                visible = text in item.text(0).lower()
                item.setHidden(not visible)
                visible_category |= visible

            category.setHidden(not visible_category)
            category.setExpanded(True)

    def on_item_activated(self, item, column):
        node_type = item.data(0, Qt.UserRole)
        if not node_type:
            return

        self._node_chosen = True
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

    def closeEvent(self, event):
        if not self._node_chosen:
            view = self.parent()
            if view:
                scene = view.scene()
                if scene and scene.drag_edge:
                    scene._cancel_drag_edge()
        super().closeEvent(event)
