# about.py
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

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
)

from core.config import MarkdownLoader
from core.debug import Info
from core.traduction import Traduction
from themes.theme_manager import Theme
from ui.about.about_pages import AboutMainPage, AboutTextPage


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setModal(True)
        if Info.get_device_type() == "phone":
            self.showMaximized()
        else:
            self.resize(380, 750)
        self.setMinimumSize(360, 294)
        self.setWindowTitle(Traduction.get_trad("about", "About"))

        self.current_index = 0
        self.animations = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("AboutScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stack = QStackedWidget()
        self.stack.setContentsMargins(10, 0, 10, 2)
        self.scroll_area.setWidget(self.stack)

        self.pages = {}
        self.pages["main"] = AboutMainPage(self.go_to)
        self.pages["credits"] = AboutTextPage(
            "about_credits", "Credits", MarkdownLoader.load_markdown("CREDITS.md")
        )
        self.pages["legal"] = AboutTextPage(
            "about_legal", "Legal", MarkdownLoader.load_markdown("LICENSE.md")
        )
        self.pages["whats_new"] = AboutTextPage(
            "about_whats_new", "What's New", MarkdownLoader.load_markdown("WHATSNEW.md")
        )

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.pages["main"])
        self.current_index = self.stack.currentIndex()

        self.back_button = QPushButton(Traduction.get_trad("back", "Back"))
        self.back_button.setFixedHeight(40)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setStyleSheet(pushbutton_style())
        self.back_button.hide()

        close_button = QPushButton(Traduction.get_trad("close", "Close"))
        close_button.setFixedHeight(40)
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(pushbutton_style())

        footer = QHBoxLayout()
        footer.addWidget(self.back_button)
        footer.addWidget(close_button)
        footer.setContentsMargins(0, 0, 10, 10)

        main_layout.addSpacing(10)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(footer)
        self._apply_theme()

    def show_back_button(self):
        self.back_button.show()

    def hide_back_button(self):
        self.back_button.hide()

    def animate_switch(self, target_index, direction):
        current = self.stack.currentWidget()
        target = self.stack.widget(target_index)

        w = self.stack.width()
        target.move(direction * w, 0)
        target.show()

        anim_out = QPropertyAnimation(current, b"pos", self)
        anim_out.setDuration(220)
        anim_out.setStartValue(QPoint(0, 0))
        anim_out.setEndValue(QPoint(-direction * w, 0))
        anim_out.setEasingCurve(QEasingCurve.OutCubic)

        anim_in = QPropertyAnimation(target, b"pos", self)
        anim_in.setDuration(220)
        anim_in.setStartValue(QPoint(direction * w, 0))
        anim_in.setEndValue(QPoint(0, 0))
        anim_in.setEasingCurve(QEasingCurve.InOutQuad)

        def finish():
            self.stack.setCurrentIndex(target_index)
            current.move(0, 0)
            target.move(0, 0)
            self.current_index = target_index
            if self.current_index == 0:
                self.hide_back_button()
            else:
                self.show_back_button()

        anim_in.finished.connect(finish)

        anim_out.start()
        anim_in.start()
        self.animations = [anim_out, anim_in]

    def go_to(self, name):
        target_index = self.stack.indexOf(self.pages[name])
        if target_index == self.current_index:
            return
        self.animate_switch(target_index, 1)

    def go_back(self):
        if self.current_index == 0:
            return
        self.animate_switch(0, -1)

    def _apply_theme(self):
        self.scroll_area.setStyleSheet(scroll_style())
        self.setStyleSheet(main_style())


def main_style() -> str:
    return f"""
            background: {Theme.get_color("ABOUT-BACKGROUND")};
            color: {Theme.get_color("ABOUT-TEXT")};
        """


def pushbutton_style() -> str:
    return f"""
            QPushButton {{
                color: {Theme.get_color("ABOUT-PUSHBUTTON_TEXT")};
                border-radius: 16px;
                background: {Theme.get_color("ABOUT-PUSHBUTTON_BACKGROUND")};
                border: 1px solid {Theme.get_color("ABOUT-PUSHBUTTON_BORDER")};
                font-size: 15px;
                border-radius: 5px;
                margin-left: 10px;
                outline: none;
            }}
            QPushButton:hover {{
                background: {Theme.get_color("ABOUT-PUSHBUTTON_HOVER")};
                border: 1px solid {Theme.get_color("ABOUT-PUSHBUTTON_BORDER_HOVER")};
            }}
            QPushButton:pressed {{
                background: {Theme.get_color("ABOUT-PUSHBUTTON_BACKGROUND_PRESSED")};
            }}
        """


def scroll_style() -> str:
    return f"""
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
