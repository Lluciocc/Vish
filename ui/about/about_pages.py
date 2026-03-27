from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QTextBrowser
)
from PySide6.QtCore import Qt
from core.traduction import Traduction
from core.serializer import Serializer
import webbrowser
from theme.theme import Theme


class AboutRow(QWidget):
    def __init__(self, text, icon, callback):
        super().__init__()
        self.callback = callback

        self.setObjectName("AboutRow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        label = QLabel(text)
        label.setStyleSheet("font-size: 14px;")
        layout.addWidget(label)

        layout.addStretch()

        arrow = QLabel(icon)
        arrow.setStyleSheet("font-size: 16px; opacity: 0.7;")
        layout.addWidget(arrow)

        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        arrow.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setStyleSheet(f"""
            QWidget#AboutRow {{
                background-color: {Theme.BUTTON};
            }}
            QWidget#AboutRow:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
            QWidget#AboutRow QLabel {{
                background: transparent;
            }}
        """)


    def mousePressEvent(self, event):
        if self.callback:
            self.callback()


class AboutGroup(QWidget):
    RADIUS = 14

    def __init__(self):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255,255,255,0.04);
                border-radius: {self.RADIUS}px;
            }}
        """)

    def add_row(self, row: QWidget):
        count = self.layout().count()

        if count == 0:
            row.setStyleSheet(row.styleSheet() + f"""
                QWidget {{
                    border-top-left-radius: {self.RADIUS}px;
                    border-top-right-radius: {self.RADIUS}px;
                }}
            """)

        self.layout().addWidget(row)

    def finalize(self):
        if self.layout().count() == 0:
            return

        last = self.layout().itemAt(self.layout().count() - 1).widget()
        last.setStyleSheet(last.styleSheet() + f"""
            QWidget {{
                border-bottom-left-radius: {self.RADIUS}px;
                border-bottom-right-radius: {self.RADIUS}px;
            }}
        """)


def section_title(key, fallback):
    label = QLabel(Traduction.get_trad(key, fallback))
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 22px; font-weight: 600;")
    return label


def subtitle(key, fallback):
    label = QLabel(Traduction.get_trad(key, fallback))
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("opacity: 0.75;")
    return label


class AboutMainPage(QWidget):
    def __init__(self, go_to):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        root.addWidget(section_title("app_name", "Visual Bash Editor"))
        root.addWidget(subtitle(
            "app_tagline",
            "A visual way to build Bash scripts"
        ))

        version = QLabel(Serializer.VERSION)
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("""
            QLabel {
                padding: 4px 14px;
                min-height: 28px;
                border-radius: 9px;
                background-color: #2c3e50;
                color: #8cc2ff;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        vrow = QHBoxLayout()
        vrow.addStretch()
        vrow.addWidget(version)
        vrow.addStretch()
        root.addLayout(vrow)

        root.addSpacing(8)

        g1 = AboutGroup()
        g1.add_row(AboutRow(
            Traduction.get_trad("about_whats_new", "What's New"),
            "›",
            lambda: go_to("whats_new")
        ))
        g1.add_row(AboutRow(
            Traduction.get_trad("about_website", "Website"),
            "↗",
            lambda: webbrowser.open("https://lluciocc.fr")
        ))
        g1.finalize()
        root.addWidget(g1)

        g2 = AboutGroup()
        g2.add_row(AboutRow(
            Traduction.get_trad("about_theme_repo", "Themes Collection Repository"),
            "↗",
            lambda: webbrowser.open("https://github.com/Lluciocc/vish-theme-collection")
        ))
        g2.add_row(AboutRow(
            Traduction.get_trad("about_questions", "Frequently Asked Questions"),
            "↗",
            lambda: webbrowser.open("https://github.com/Lluciocc/Vish/wiki#faqs")
        ))
        g2.add_row(AboutRow(
            Traduction.get_trad("about_report", "Report an Issue"),
            "↗",
            lambda: webbrowser.open("https://github.com/Lluciocc/Vish/issues")
        ))
        g2.add_row(AboutRow(
            Traduction.get_trad("about_support", "Support the project"),
            "↗",
            lambda: webbrowser.open("https://github.com/Lluciocc/Vish?sponsor=1")
        ))
        g2.finalize()
        root.addWidget(g2)

        g3 = AboutGroup()
        g3.add_row(AboutRow(
            Traduction.get_trad("about_credits", "Credits"),
            "›",
            lambda: go_to("credits")
        ))
        g3.add_row(AboutRow(
            Traduction.get_trad("about_legal", "Legal"),
            "›",
            lambda: go_to("legal")
        ))
        g3.finalize()
        root.addWidget(g3)

        root.addStretch()


class AboutTextPage(QWidget):
    def __init__(self, title_key, fallback, text):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel(Traduction.get_trad(title_key, fallback))
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        content = QTextBrowser()
        content.setMarkdown(text)
        content.setOpenExternalLinks(True)
        content.setFrameShape(QTextBrowser.NoFrame)

        content.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content.document().setDocumentMargin(0)

        content.setStyleSheet("""
        QTextBrowser {
            background: transparent;
            border: none;
            padding: 0;
            opacity: 0.85;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 2px;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 120);
            min-height: 30px;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 160);
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            background: none;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """)

        layout.addWidget(content)
