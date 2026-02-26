from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QEasingCurve

# test 3
class MessageWidget(QWidget):
    STYLES = {
        "error": """
            QWidget {
                background: #d63031;
                border: 1px solid #b02324;
                border-radius: 10px;
            }
        """,
        "warn": """
            QWidget {
                background: #f39c12;
                border: 1px solid #d68910;
                border-radius: 10px;
            }
        """,
        "info": """
            QWidget {
                background: #2e86c1;
                border: 1px solid #1f618d;
                border-radius: 10px;
            }
        """
    }

    TITLE_COLORS = {
        "error": "#ffc7c7",
        "warn":  "#ffe5bb",
        "info":  "#c8e0ff",
    }

    def __init__(self, parent, message: str, level="info"):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self.STYLES.get(level, self.STYLES["info"]))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        title = QLabel(level.upper())
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
                color: {self.TITLE_COLORS.get(level, "#ffffff")};
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        layout.addWidget(title)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: white;
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        layout.addWidget(label)

        self.adjustSize()


    def show_animated(self):
        parent = self.parent()
        if not parent:
            return

        margin = 20
        y = parent.height() - self.height() - margin

        start = QPoint(parent.width(), y)
        visible = QPoint(parent.width() - self.width() - margin, y)
        end = QPoint(parent.width(), y)

        self.move(start)
        self.show()

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(250)
        self.anim.setStartValue(start)
        self.anim.setEndValue(visible)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

        QTimer.singleShot(3000, lambda: self._hide(end))

    def _hide(self, end):
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.finished.connect(self.close)
        self.anim.start()

