from PySide6.QtSvgWidgets import QGraphicsSvgItem, QSvgWidget
from PySide6.QtGui import QIcon
from theme.theme import Theme
from core.debug import Info
import os


class Path:
    def get_path(category, icon_name):
        category = category.lower().replace(" ", "_")
        icon_name = icon_name.lower().replace(" ", "_")

        contrast = Theme.type
        icon_path = Info.resource_path(f"assets/icons/{category}/{icon_name}.svg")
        if not os.path.exists(icon_path):
            icon_path = Info.resource_path(f"assets/icons/{category}/{contrast}/{icon_name}.svg")
            if not os.path.exists(icon_path):
                icon_path = Info.resource_path(f"assets/icons/{category}/{icon_name}_placeholder.svg")
                if not os.path.exists(icon_path):
                    icon_path = Info.resource_path(f"assets/icons/{category}/{contrast}/{icon_name}_placeholder.svg")
                    if not os.path.exists(icon_path):
                        icon_path = Info.resource_path(f"assets/icons/placeholder.svg")
        return icon_path


class Icon:
    def load_icon(category, name):
        icon_path = Path.get_path(category, name)
        icon = QIcon(icon_path)
        return icon

    def load_item(self, category, name, size, padding):
        icon_path = Path.get_path(category, name)
        icon = QGraphicsSvgItem(icon_path, self)

        bounds = icon.boundingRect()
        scale = size / max(bounds.width(), bounds.height())
        icon.setScale(scale)
        icon_y = (self.HEADER_HEIGHT - bounds.height() * scale) / 2
        icon.setPos(padding, icon_y)

    def load_widget(self, category, name, width, height):
        icon_path = Path.get_path(category, name)
        icon = QSvgWidget(icon_path, self)
        icon.setFixedSize(width, height)
