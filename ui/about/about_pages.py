# about_pages.py
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
from core.serializer import Serializer
from core.traduction import Traduction
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QTextBrowser, QVBoxLayout, QWidget
from themes.theme_manager import Theme
from ui.modal import Modal
import webbrowser


def open_link_box(link_name, link):
    text = f"Do you want to open: {link_name}?\n\n{link}\n"
    question = Modal.create("open_link", None, text)

    if question == "yes":
        webbrowser.open(link)
    elif question == "ok":
        QApplication.clipboard().setText(link)


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
        layout.addWidget(arrow)

        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        arrow.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setStyleSheet(pushbutton_style())
        arrow.setStyleSheet(arrow_label_style())

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
                background-color: {Theme.get_color("ABOUT_PAGES-BUTTONGROUP_BACKGROUND")};
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
    label.setWordWrap(True)
    return label

def subtitle(key, fallback):
    label = QLabel(Traduction.get_trad(key, fallback))
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("opacity: 0.75;")
    label.setWordWrap(True)
    return label


class AboutMainPage(QWidget):
    def __init__(self, go_to):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 11, 0, 0)
        root.setSpacing(18)

        icon = QSvgWidget(Icon.load_widget(self, None, "Vish", 128, 128))
        icon.setMinimumWidth(128)
        icon.setStyleSheet("background: transparent")

        title_key = "app_name"
        title_fallback = "Visual Bash Editor"
        subtitle_key = "app_tagline"
        subtitle_fallback = "A visual way to build Bash scripts"

        version = QLabel(Serializer.VERSION)
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(version_label_style())

        vrow = QHBoxLayout()
        vrow.addWidget(version)
        vrow.addStretch()

        header_text = QVBoxLayout()
        header = QHBoxLayout()
        header.addWidget(icon)
        header_text.addWidget(section_title(title_key, title_fallback))
        header_text.addWidget(subtitle(subtitle_key,subtitle_fallback))
        header_text.addLayout(vrow)
        header.addLayout(header_text)
        header.addStretch(1)
        root.addLayout(header)

        g1 = AboutGroup()
        g1.add_row(AboutRow(
            Traduction.get_trad("about_whats_new", "What's New"),
            "›",
            lambda: go_to("whats_new")
        ))
        g1.add_row(AboutRow(
            Traduction.get_trad("about_website", "Website"),
            "↗",
            lambda: open_link_box(Traduction.get_trad("about_website", "Website"), "https://lluciocc.fr")
        ))
        g1.finalize()

        g2 = AboutGroup()
        g2.add_row(AboutRow(
            Traduction.get_trad("about_theme_repo", "Themes Collection Repository"),
            "↗",
            lambda: open_link_box(Traduction.get_trad("about_theme_repo", "Themes Collection Repository"), "https://github.com/Lluciocc/vish-theme-collection")
        ))
        g2.add_row(AboutRow(
            Traduction.get_trad("about_questions", "Frequently Asked Questions"),
            "↗",
            lambda: open_link_box(Traduction.get_trad("about_questions", "Frequently Asked Questions"), "https://github.com/Lluciocc/Vish/wiki#faqs")
        ))
        g2.add_row(AboutRow(
            Traduction.get_trad("about_report", "Report an Issue"),
            "↗",
            lambda: open_link_box(Traduction.get_trad("about_report", "Report an Issue"), "https://github.com/Lluciocc/Vish/issues")
        ))
        g2.add_row(AboutRow(
            Traduction.get_trad("about_support", "Support the project"),
            "↗",
            lambda: open_link_box(Traduction.get_trad("about_support", "Support the project"), "https://github.com/Lluciocc/Vish?sponsor=1")
        ))
        g2.finalize()

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
        g3.add_row(AboutRow(
            Traduction.get_trad("about_matrix", "Join our Matrix room"),
            "↗",
            lambda: open_link_box(Traduction.get_trad("about_matrix", "Join our Matrix room"), "https://matrix.to/#/%23vish-support%3Amatrix.org")
        ))
        g3.finalize()

        root.addSpacing(8)
        root.addWidget(g1)
        root.addWidget(g2)
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

        content = QTextBrowser()
        content.setMarkdown(text)
        content.setOpenExternalLinks(True)
        content.setFrameShape(QTextBrowser.NoFrame)

        content.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content.document().setDocumentMargin(0)

        content.setStyleSheet(content_browser_style())

        layout.addWidget(title)
        layout.addWidget(content)


def pushbutton_style() -> str:
    return f"""
            QWidget#AboutRow {{
                background: {Theme.get_color("ABOUT_PAGES-PUSHBUTTON_BACKGROUND")};
            }}
            QWidget#AboutRow:hover {{
                background: {Theme.get_color("ABOUT_PAGES-PUSHBUTTON_BACKGROUND_HOVER")};
            }}
            QWidget#AboutRow QLabel {{
                background: transparent;
                color: {Theme.get_color("ABOUT_PAGES-LABEL_TEXT")};
            }}
        """

def content_browser_style() -> str:
    return f"""
            QTextBrowser {{
                border: none;
                color: {Theme.get_color("ABOUT_PAGES-BROWSER_TEXT")};
                padding: 0;
                opacity: 0.85;
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

def arrow_label_style() -> str:
    return f"""
                font-size: 16px;
                opacity: 0.7;
                color: {Theme.get_color("ABOUT_PAGES-ARROWLABEL_TEXT")};
        """

def version_label_style() -> str:
    return f"""
            QLabel {{
                padding: 4px 14px;
                min-height: 28px;
                border-radius: 9px;
                background-color: {Theme.get_color("ABOUT_PAGES-VERSIONLABEL_BACKGROUND")};;
                color: {Theme.get_color("ABOUT_PAGES-VERSIONLABEL_TEXT") if Theme.icons == 'dark' else Theme.get_color("ABOUT_PAGES-VERSIONLABEL_TEXT_INVERT")}; /*ensure good contrast*/
                font-size: 13px;
                font-weight: 600;
            }}
        """
