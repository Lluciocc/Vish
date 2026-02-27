from PySide6.QtWidgets import QApplication

class Theme:
    selected_theme = "dark"
    type = "dark"
    BACKGROUND = None
    PANEL = None
    TEXT = None
    BUTTON = None
    BUTTON_HOVER = None
    BUTTON_PRESSED = None

def set_dark_theme():
    app = QApplication.instance()
    if not app:
        return

    Theme.BACKGROUND = "#1e1e1e"
    Theme.PANEL = "#252526"
    Theme.TEXT = "#d4d4d4"
    Theme.BUTTON = "#2d2d2d"
    Theme.BUTTON_HOVER = "#3a3a3a"
    Theme.BUTTON_PRESSED = "#444444"

    app.setStyleSheet(f"""
        QWidget {{
            background-color: {Theme.PANEL};
            color: {Theme.TEXT};
            font-size: 13px;
        }}

        QPushButton {{
            background-color: {Theme.BUTTON};
            border: 1px solid #3c3c3c;
            padding: 6px 10px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {Theme.BUTTON_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {Theme.BUTTON_PRESSED};
        }}

        QTextEdit {{
            background-color: {Theme.PANEL};
            border: 1px solid #3c3c3c;
        }}

        QSplitter::handle {{
            background-color: #3c3c3c;
        }}
    """)
    Theme.selected_theme = "dark"
    Theme.type = "dark"

def set_white_theme():
    app = QApplication.instance()
    if not app:
        return

    Theme.BACKGROUND = "#f5f5f5"
    Theme.PANEL = "#ffffff"
    Theme.TEXT = "#1e1e1e"
    Theme.BUTTON = "#e0e0e0"
    Theme.BUTTON_HOVER = "#d5d5d5"
    Theme.BUTTON_PRESSED = "#c8c8c8"

    app.setStyleSheet(f"""
        QWidget {{
            background-color: {Theme.PANEL};
            color: {Theme.TEXT};
            font-size: 13px;
        }}

        QPushButton {{
            background-color: {Theme.BUTTON};
            border: 1px solid #b0b0b0;
            padding: 6px 10px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {Theme.BUTTON_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {Theme.BUTTON_PRESSED};
        }}

        QTextEdit {{
            background-color: {Theme.PANEL};
            border: 1px solid #c0c0c0;
        }}

        QSplitter::handle {{
            background-color: #c0c0c0;
        }}
    """)
    Theme.selected_theme = "white"
    Theme.type = "light"

def set_purple_theme():
    app = QApplication.instance()
    if not app:
        return

    Theme.BACKGROUND = "#2b1b3f"
    Theme.PANEL = "#35204f"
    Theme.TEXT = "#e6d9ff"
    Theme.BUTTON = "#4b2c72"
    Theme.BUTTON_HOVER = "#5a3690"
    Theme.BUTTON_PRESSED = "#6a41b0"

    app.setStyleSheet(f"""
        QWidget {{
            background-color: {Theme.PANEL};
            color: {Theme.TEXT};
            font-size: 13px;
        }}

        QPushButton {{
            background-color: {Theme.BUTTON};
            border: 1px solid #6a41b0;
            padding: 6px 10px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {Theme.BUTTON_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {Theme.BUTTON_PRESSED};
        }}

        QTextEdit {{
            background-color: {Theme.PANEL};
            border: 1px solid #6a41b0;
        }}

        QSplitter::handle {{
            background-color: #6a41b0;
        }}
    """)
    Theme.selected_theme = "dark"
    Theme.type = "dark"

def set_breeze_dark_theme():
    app = QApplication.instance()
    if not app:
        return

    Theme.BACKGROUND = "#141618"
    Theme.PANEL = "#292C30"
    Theme.TEXT = "#FCFCFC"
    Theme.BUTTON = "#57595C"
    Theme.BUTTON_HOVER = "#3584E4"
    Theme.BUTTON_PRESSED = "#3584E4"

    app.setStyleSheet(f"""
        QWidget {{
            background-color: {Theme.PANEL};
            color: {Theme.TEXT};
            font-size: 13px;
        }}

        QPushButton {{
            background-color: {Theme.PANEL};
            border: 1px solid {Theme.BUTTON};
            padding: 6px 10px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            border-color: {Theme.BUTTON_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {Theme.BUTTON_PRESSED};
        }}

        QTextEdit {{
            background-color: {Theme.BACKGROUND};
            border: 1px solid {Theme.BUTTON};
        }}

        QSplitter::handle {{
            background-color: {Theme.BUTTON};
        }}
    """)
    Theme.selected_theme = "dark"
    Theme.type = "dark"
