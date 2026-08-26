# palette.py
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

from core.icons import Icon
from core.traduction import Traduction
from nodes.registry import NODE_REGISTRY
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QFrame
from themes.theme_manager import Theme
import os


links = {}


class CustomQLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        key_code = event.key()
        if (key_code == Qt.Key_Up or key_code == Qt.Key_Down):
            self.parent().parent().keyPressEventArrow(event)

        super().keyPressEvent(event)


class CustomQTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        # if the user manually switches into the tree we want to 
        # allow selection of the category 
        if (not self.parent().parent().search_input.hasFocus()):
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
        self.setWindowFlags(Qt.Popup)

        self.background = QWidget(self)
        self.background.setObjectName("Background")
        self.background.resize(320, 420)

        self.search_input = CustomQLineEdit(self)
        self.search_input.setPlaceholderText(Traduction.get_trad("search_nodes", "Search nodes..."))
        self.search_input.textChanged.connect(self.filter_nodes)

        self.tree = CustomQTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_item_activated)
        self.tree.setMouseTracking(True)
        self.tree.viewport().setMouseTracking(True)
        self.tree.setIndentation(10)
        self.tree.setAlternatingRowColors(True)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(separator_style())

        layout = QVBoxLayout(self.background)
        layout.addWidget(self.search_input)
        layout.addWidget(separator)
        layout.addWidget(self.tree)

        self._node_chosen = False
        self.populate_tree()
        self.setStyleSheet(tree_style())

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
            icon = self.get_icon(links[category])
            cat_item.setIcon(0, icon)

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
                if scene and scene.drag_edges:
                    scene.restore_pending_connection()
        super().closeEvent(event)

    def get_icon(self, name):
        icon = Icon.load_icon("menu_graph", name)
        return icon


def separator_style() -> str:
    return f"""
            QFrame[frameShape="4"] {{
                border: none;
                max-height: 1px;
                background: {Theme.get_color("PALETTE-SEPARATOR")};
            }}
        """

def tree_style() -> str:
    return f"""
            QWidget {{
                background: transparent;
            }}
            QWidget#Background {{
                background: {Theme.get_color("PALETTE-BACKGROUND")};
                border-radius: 12px;
                border: 1px solid {Theme.get_color("PALETTE-BORDER")};
            }}
            CustomQTreeWidget::item,
            CustomQTreeWidget {{
                selection-background-color: transparent;
                alternate-background-color: {Theme.get_color("PALETTE-BACKGROUND_ALTERNATE")};
                outline: none
            }}
            CustomQTreeWidget::item:focus,
            CustomQTreeWidget::item:selected {{
                border: 1px solid {Theme.get_color("PALETTE-BACKGROUND_HOVER")};
                border-radius: 6px;
            }}
            CustomQTreeWidget::item:hover{{
                border-bottom: 1px solid {Theme.get_color("PALETTE-BACKGROUND_HOVER")};
                border-radius: 6px;
            }}
            CustomQLineEdit {{
                border: transparent;
                margin: 0px 8px;
            }}
            QScrollArea#SettingsScrollArea {{
                background: {Theme.get_color("SCROLL_AREA")};
                border: none;
            }}
            QScrollArea#SettingsScrollArea > QWidget > QWidget {{
                background: {Theme.get_color("SCROLL_SUB_BAR")};
            }}
            QScrollBar:vertical {{
                width: 10px;
                margin: 2px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.get_color("SCROLL_HANDLE")};
                min-height: 34px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.get_color("SCROLL_HANDLE_HOVER")};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: {Theme.get_color("SCROLL_SUB_BAR")};
            }}
        """
