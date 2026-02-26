from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from nodes.registry import NODE_REGISTRY
from theme.theme import Theme
import os
from core.traduction import Traduction
from core.debug import Info

links = {}

class CustomQLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        key_code = event.key()
        if (key_code == Qt.Key_Up or key_code == Qt.Key_Down):
            self.parent().keyPressEventArrow(event)

        super().keyPressEvent(event)

        
class CustomQTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        # if the user manually switches into the tree we want to 
        # allow selection of the category 
        if (not self.parent().search_input.hasFocus()):
            return

        # if a category is selected after the keyPressEvent,
        # reapply the event to go in the same direction again
        current_item = self.currentItem()
        for i in range(self.topLevelItemCount()):
            category = self.topLevelItem(i)
            if (current_item == category):
                super().keyPressEvent(event)
                return

        
class NodePalette(QWidget):
    node_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Traduction.get_trad("add_node", "Add Node"))
        self.resize(320, 420)
        self.setWindowFlags(Qt.Popup)

        layout = QVBoxLayout(self)

        self.search_input = CustomQLineEdit(self)
        self.search_input.setPlaceholderText(Traduction.get_trad("search_nodes", "Search nodes..."))
        self.search_input.textChanged.connect(self.filter_nodes)
        layout.addWidget(self.search_input)

        self.tree = CustomQTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_item_activated)
        self.tree.setMouseTracking(True)
        self.tree.viewport().setMouseTracking(True)
        layout.addWidget(self.tree)

        self._node_chosen = False
        self.populate_tree()

    def keyPressEventArrow(self, event):
        self.tree.keyPressEvent(event)
        return

    def populate_tree(self):
        self.tree.clear()

        categories = {}

        for node_type, meta in NODE_REGISTRY.items():
            cat = Traduction.get_trad(meta["category"], meta["category"])
            links[cat] = meta["category"]
            categories.setdefault(cat, []).append(
                (
                    Traduction.get_trad(f"{meta["label"]}_label", meta["label"]),
                    node_type,
                    Traduction.get_trad(f"{meta["label"]}_desc",meta.get("description", ""))
                )
            )

        for category in sorted(categories.keys()):
            cat_item = QTreeWidgetItem([category])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)
            cat_item.setExpanded(True)
            ico = self.get_icon(links[category])
            if ico:
                cat_item.setIcon(0, ico)

            for label, node_type, description in sorted(categories[category]):
                item = QTreeWidgetItem([Traduction.get_trad(f"{node_type}_label", label)])
                item.setData(0, Qt.UserRole, node_type)
                item.setToolTip(0, Traduction.get_trad(f"{node_type}_desc",description))
                cat_item.addChild(item)

            self.tree.addTopLevelItem(cat_item)

    def filter_nodes(self, text):
        text = text.lower()

        first_Visible_item = None; 
        for i in range(self.tree.topLevelItemCount()):
            category = self.tree.topLevelItem(i)
            visible_category = False

            for j in range(category.childCount()):
                item = category.child(j)
                visible = text in item.text(0).lower()
                item.setHidden(not visible)
                visible_category |= visible
                if visible and (first_Visible_item is None):
                    first_Visible_item = item

            category.setHidden(not visible_category)
            category.setExpanded(True)

        self.tree.setCurrentItem(first_Visible_item)

    def on_item_activated(self, item, column):
        node_type = item.data(0, Qt.UserRole)
        if not node_type:
            return

        self._node_chosen = True
        self.node_selected.emit(node_type)
        self.close()

    def focusOutEvent(self, event):
        if(not (self.search_input.hasFocus())):
            self.close()
        super().focusOutEvent(event)
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self.tree.currentItem():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
        self.search_input.setFocus()


    def keyPressEvent(self, event):
        key = event.key()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            item = self.tree.currentItem()
            if not item:
                return

            if item.isExpanded():
                item.setExpanded(False)
                return
            
            if item.childCount() > 0:
                item.setExpanded(True)
                if item.childCount() > 0:
                    self.tree.setCurrentItem(item.child(0))
                return

            node_type = item.data(0, Qt.UserRole)
            if node_type:
                self._node_chosen = True
                self.node_selected.emit(node_type)
                self.close()
                return

        if key == Qt.Key_Escape:
            self.close()
            return

        super().keyPressEvent(event)

    def closeEvent(self, event):
        if not self._node_chosen:
            view = self.parent()
            if view:
                scene = view.scene()
                if scene and scene.drag_edge:
                    scene._cancel_drag_edge()
        super().closeEvent(event)

    def get_icon(self, category):
        theme = Theme.type
        path = Info.resource_path(f"assets/icons/{theme}/{category.lower().replace(' ', '_')}.png")
        if os.path.exists(path):
            return QIcon(path)
        return None