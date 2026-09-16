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

import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QMouseEvent,
    QTextBlockFormat,
    QTextCharFormat,
    QColor,
    QTextTableFormat,
    QTextCursor
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QToolTip
)

from core.debug import Info
from core.icons import Icon
from core.serializer import Serializer
from core.traduction import Traduction
from themes.theme_manager import Theme
from ui.modal import Modal


def open_link_box(parent, link_name, link):
    text = f"Do you want to open: {link_name}?\n\n{link}\n"
    question = Modal.create("open_link", parent, text)

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
            row.setStyleSheet(
                row.styleSheet()
                + f"""
                QWidget {{
                    border-top-left-radius: {self.RADIUS}px;
                    border-top-right-radius: {self.RADIUS}px;
                }}
            """
            )

        self.layout().addWidget(row)

    def finalize(self):
        if self.layout().count() == 0:
            return

        last = self.layout().itemAt(self.layout().count() - 1).widget()
        last.setStyleSheet(
            last.styleSheet()
            + f"""
            QWidget {{
                border-bottom-left-radius: {self.RADIUS}px;
                border-bottom-right-radius: {self.RADIUS}px;
            }}
        """
        )


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
        root.setContentsMargins(0, 11, 10, 0)
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
        header_text.addWidget(subtitle(subtitle_key, subtitle_fallback))
        header_text.addLayout(vrow)
        header.addLayout(header_text)
        header.addStretch(1)
        root.addLayout(header)

        g1 = AboutGroup()
        g1.add_row(
            AboutRow(
                Traduction.get_trad("about_whats_new", "What's New"),
                "›",
                lambda: go_to("whats_new"),
            )
        )
        g1.add_row(
            AboutRow(
                Traduction.get_trad("about_website", "Website"),
                "↗",
                lambda: open_link_box(
                    self,
                    Traduction.get_trad("about_website", "Website"),
                    "https://lluciocc.fr",
                ),
            )
        )
        g1.finalize()

        g2 = AboutGroup()
        g2.add_row(
            AboutRow(
                Traduction.get_trad("about_theme_repo", "Themes Collection Repository"),
                "↗",
                lambda: open_link_box(
                    self,
                    Traduction.get_trad(
                        "about_theme_repo", "Themes Collection Repository"
                    ),
                    "https://github.com/Lluciocc/vish-theme-collection",
                ),
            )
        )
        g2.add_row(
            AboutRow(
                Traduction.get_trad("about_questions", "Frequently Asked Questions"),
                "↗",
                lambda: open_link_box(
                    self,
                    Traduction.get_trad(
                        "about_questions", "Frequently Asked Questions"
                    ),
                    "https://github.com/Lluciocc/Vish/wiki#faqs",
                ),
            )
        )
        g2.add_row(
            AboutRow(
                Traduction.get_trad("about_report", "Report an Issue"),
                "↗",
                lambda: open_link_box(
                    self,
                    Traduction.get_trad("about_report", "Report an Issue"),
                    "https://github.com/Lluciocc/Vish/issues",
                ),
            )
        )
        g2.add_row(
            AboutRow(
                Traduction.get_trad("about_support", "Support the project"),
                "↗",
                lambda: open_link_box(
                    self,
                    Traduction.get_trad("about_support", "Support the project"),
                    "https://github.com/Lluciocc/Vish?sponsor=1",
                ),
            )
        )
        g2.finalize()

        g3 = AboutGroup()
        g3.add_row(
            AboutRow(
                Traduction.get_trad("about_credits", "Credits"),
                "›",
                lambda: go_to("credits"),
            )
        )
        g3.add_row(
            AboutRow(
                Traduction.get_trad("about_legal", "Legal"), "›", lambda: go_to("legal")
            )
        )
        g3.add_row(
            AboutRow(
                Traduction.get_trad("about_matrix", "Join our Matrix room"),
                "↗",
                lambda: open_link_box(
                    self,
                    Traduction.get_trad("about_matrix", "Join our Matrix room"),
                    "https://matrix.to/#/%23vish-support%3Amatrix.org",
                ),
            )
        )
        g3.finalize()

        root.addSpacing(8)
        root.addWidget(g1)
        root.addWidget(g2)
        root.addWidget(g3)
        root.addStretch()


class AboutTextPage(QTextEdit):
    def __init__(self, md_file):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setStyleSheet("padding-right: 10")
        self.setReadOnly(True)
        self.setFrameShape(QTextEdit.NoFrame)
        self.setMouseTracking(True)
        self.mouse_cursor = "default"
        self.old_anchor = ""
        self.cursor = self.textCursor()
        self.create_document(md_file)

    def create_document(self, md_file):
        block_text_state = "ignore"
        block_text = ""
        inset = 0
        remove_empty = False
        link_pos = []

        self.cursor.insertBlock()
        self.cursor.insertBlock()

        with open(Info.resource_path(f"assets/markdown/{md_file}.md"), "r") as file:
            for line in file:
                line = line.replace("->", "→")
                if line == "\n":
                    if remove_empty:
                        remove_empty = False
                        continue
                    block_text_state = "initial"
                    self.formating("normal")
                    if block_text != "":
                        block_text.strip()
                        if inset == 0:
                            self.formating("normal")
                            self.cursor.insertText(block_text)
                            self.cursor.insertBlock()
                        elif inset == 1:
                            self.formating("normal_in_1")
                            self.cursor.insertText(block_text)
                            self.cursor.insertBlock()
                        elif inset == 2:
                            cell = table.cellAt(table.rows() - 1, 1)
                            self.cursor = cell.firstCursorPosition()
                            self.formating("normal")
                            self.cursor.insertText(block_text)
                            self.cursor = self.textCursor()
                            inset = 1
                        elif inset == 3:
                            self.formating("center_text")
                            self.cursor.insertText(block_text)
                            self.cursor.insertBlock()
                            inset = 0

                        block_text = ""
                    self.cursor.insertBlock()
                    continue

                elif block_text_state == "initial" and line.startswith("  "):
                    block_text_state = "add"
                elif block_text_state != "add":
                    block_text_state = "ignore"

                if line.startswith("###"):
                    self.formating("h3")
                    self.cursor.insertText(f"{line.split("### ")[1]}")
                    inset = 0
                elif line.startswith("##  "):
                    self.formating("h2_center")
                    self.cursor.insertText(f"{line.split("## ")[1]}")
                    inset = 0
                elif line.startswith("##"):
                    self.formating("h2")
                    self.cursor.insertText(f"{line.split("## ")[1]}")
                    inset = 0
                elif line.startswith("#"):
                    self.formating("h1")
                    self.cursor.insertText(f"{line.split("# ")[1]}")
                    inset = 0
                elif line.startswith("      "):
                    self.formating("center")
                    self.cursor.insertText(f"{line.split("      ")[1]}")
                    inset = 0
                else:
                    self.formating("normal")

                    line_split = line.split(".", 1)
                    if self.is_int(line.split(".", 1)[0]):
                        if len(line_split[0].split("    ")) == 1:
                            self.formating("numeric")
                            self.cursor.insertText(line_split[0].strip() + ".  " + line_split[1])
                            inset = 1
                            remove_empty = True
                            continue

                    elif self.is_letter(line.split(")", 1)[0]):

                        table_format = QTextTableFormat()
                        table_format.setLeftMargin(5)
                        table = self.cursor.insertTable(1, 2, table_format)

                        cell = table.cellAt(table.rows() - 1, 0)
                        self.cursor = cell.firstCursorPosition()
                        self.formating("alpha_numeric")
                        self.cursor.insertText(line.split(")", 1)[0].strip() + ")")
                        self.cursor = self.textCursor()

                        line = line.split(")", 1)[1].strip()
                        inset = 2

                    elif line.startswith("    ") and inset != 2:
                        inset = 3


                    line_split = line.split("[")
                    if len(line_split) > 1:
                        for index in range(len(line_split) - 1):
                            text_split = line_split[index + 1].split("](", 1)
                            if len(text_split) > 1:
                                link_split = text_split[1].split(")", 1)
                                if len(link_split) > 1:
                                    link_text = text_split[0]
                                    url = link_split[0]

                                    if block_text_state == "add":
                                        if index == 0:
                                            line = line_split[0].strip().replace("  ", " ")
                                            block_text = block_text.strip() + line_split[0].strip() + " "
                                        else:
                                            line = line_split[index].split(")", 1)[1].strip().replace("  ", " ")
                                            block_text = block_text.strip() + line_split[index].split(")", 1)[1] + " "

                                        if inset == 3:
                                            link_pos.insert(0, (self.cursor.position() + len(block_text), link_text.strip(), url, "link_center"))
                                        else:
                                            link_pos.insert(0, (self.cursor.position() + len(block_text), link_text.strip(), url, "link"))

                                        if index == len(line_split) - 2:
                                            block_text = block_text + link_split[1].split("\n")[0] + " "

                                    else:
                                        self.formating("normal")
                                        if index == 0:
                                            self.cursor.insertText(line_split[0])
                                        else:
                                            self.cursor.insertText(line_split[index].split(")", 1)[1])

                                        self.formating("link", f"{link_text}\\{url}")
                                        self.cursor.insertText(link_text)

                                        if index == len(line_split) - 2:
                                            self.formating("normal")
                                            self.cursor.insertText(link_split[1])

                                else:
                                    if block_text_state == "add":
                                        line = line.strip().replace("  ", " ")
                                        block_text = block_text + line.split("\n")[0] + " "
                                    else:
                                        self.cursor.insertText(line)
                            else:
                                if block_text_state == "add":
                                    line = line.strip().replace("  ", " ")
                                    block_text = block_text + line.split("\n")[0] + " "
                                else:
                                    self.cursor.insertText(line)
                    else:
                        if block_text_state == "add":
                            line = line.strip().replace("  ", " ")
                            block_text = block_text + line.split("\n")[0] + " "
                        else:
                            self.cursor.insertText(line)

        self.moveCursor(QTextCursor.Start)
        for link in link_pos:
            self.cursor.setPosition(link[0])
            self.formating(link[3], f"{link[1]}\\{link[2]}")
            self.cursor.insertText(link[1])

    def move_top(self):
        self.moveCursor(QTextCursor.Start)

    def formating(self, get_format, link=""):
        FORMAT = {
            "normal": {
                "block": (Qt.AlignmentFlag.AlignJustify),
                "char": (10, "ABOUT_PAGES-TEXT", False, False),
            },
            "normal_in_1": {
                "block": (Qt.AlignmentFlag.AlignJustify, 10),
                "char": (10, "ABOUT_PAGES-TEXT", False, False),
            },
            "center": {
                "block": (Qt.AlignmentFlag.AlignCenter, 0),
                "char": (10, "ABOUT_PAGES-CENTER", False, False),
            },
            "center_text": {
                "block": (Qt.AlignmentFlag.AlignJustify, 15, 0, 15),
                "char": (10, "ABOUT_PAGES-CENTER_TEXT", False, False),
            },
            "numeric": {
                "block": (Qt.AlignmentFlag.AlignLeft),
                "char": (10, "ABOUT_PAGES-NUMERIC", False, False),
            },
            "alpha_numeric": {
                "block": (Qt.AlignmentFlag.AlignLeft, 0, 5),
                "char": (10, "ABOUT_PAGES-ALPHA_NUMERIC", False, False),
            },
            "link": {
                "block": (Qt.AlignmentFlag.AlignJustify),
                "char": (10, "ABOUT_PAGES-LINK", True, True),
            },
            "link_center": {
                "block": (Qt.AlignmentFlag.AlignJustify, 15, 0, 15),
                "char": (10, "ABOUT_PAGES-LINK", True, True),
            },
            "h1": {
                "block": (Qt.AlignmentFlag.AlignCenter, 0, 10),
                "char": (20, "ABOUT_PAGES-TITLE_H", True, False),
            },
            "h2_center": {
                "block": (Qt.AlignmentFlag.AlignCenter, 0, 5),
                "char": (16, "ABOUT_PAGES-TITLE_HH", False, False),
            },
            "h2": {
                "block": (Qt.AlignmentFlag.AlignLeft, 20, 5),
                "char": (16, "ABOUT_PAGES-TITLE_HH", False, False),
            },
            "h3": {
                "block": (Qt.AlignmentFlag.AlignLeft),
                "char": (14, "ABOUT_PAGES-TITLE_HHH", False, False),
            }
        }

        self.cursor.setBlockFormat(self.set_block(*FORMAT[get_format]["block"]))
        self.cursor.setCharFormat(self.set_char(*FORMAT[get_format]["char"], link))

    def set_char(self, size, color, underline, anchor, link = ""):
        char = QTextCharFormat()
        char.setFontPointSize(size)
        char.setFontUnderline(underline)
        char.setForeground(QColor(Theme.get_color(color)))
        char.setAnchor(anchor)
        if link:
            char.setAnchorHref(link)
        return char

    def set_block(self, align, left = 0, bottom = 0, right = 0):
        block = QTextBlockFormat()
        block.setAlignment(align)
        block.setLeftMargin(left)
        block.setBottomMargin(bottom)
        block.setRightMargin(right)
        return block

    def is_int(self, string):
        try:
            int(string)
            return True
        except:
            return False

    def is_letter(self, string):
        letter = string.split("    ")
        if len(letter) > 1:
            if letter[1].islower() and len(letter[1]) == 1:
                return True
            return False
        return False

    def mouseMoveEvent(self, event: QMouseEvent):
        anchor = self.anchorAt(event.pos())
        if anchor:
            if self.mouse_cursor == "default":
                self.mouse_cursor = "link_hand"
                QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)
                self.old_anchor = anchor
                QToolTip.showText(event.globalPos(), anchor.split("\\")[1], self)
            if anchor != self.old_anchor:
                self.old_anchor = anchor
                QToolTip.showText(event.globalPos(), anchor.split("\\")[1], self)
        else:
            if self.mouse_cursor == "link_hand":
                self.mouse_cursor = "default"
                QApplication.restoreOverrideCursor()
                QToolTip.hideText()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        anchor = self.anchorAt(event.pos())
        if anchor:
            open_link_box(self, anchor.split("\\")[0], anchor.split("\\")[1])
        super().mousePressEvent(event)


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
                background-color: {Theme.get_color("ABOUT_PAGES-VERSIONLABEL_BACKGROUND")};
                color: {Theme.get_color("ABOUT_PAGES-VERSIONLABEL_TEXT") if Theme.icons == "dark" else Theme.get_color("ABOUT_PAGES-VERSIONLABEL_TEXT_INVERT")}; /*ensure good contrast*/
                font-size: 13px;
                font-weight: 600;
            }}
        """
