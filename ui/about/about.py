from core.config import MarkdownLoader
from core.debug import Info
from core.traduction import Traduction
from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt
from PySide6.QtWidgets import QDialog, QGraphicsOpacityEffect, QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout
from theme.theme import Theme
from ui.about.about_pages import AboutMainPage, AboutTextPage

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setModal(True)
        if Info.get_device_type() == "phone":
            self.showMaximized()
        else:
            self.resize(440, 520)
        self.setWindowTitle(Traduction.get_trad("about", "About"))

        self.current_index = 0
        self.animations = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 20)
        main_layout.setSpacing(12)

        header = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.setEnabled(False)
        self.back_opacity = QGraphicsOpacityEffect(self.back_btn)
        self.back_opacity.setOpacity(0.0)
        self.back_btn.setGraphicsEffect(self.back_opacity)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 16px;
                background-color: rgba(255,255,255,0.06);
            }}
            QPushButton:hover {{
                background-color: {Theme.BUTTON_HOVER};
            }}
        """)

        header.addWidget(self.back_btn)
        header.addStretch()
        main_layout.addLayout(header)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.pages = {}

        self.pages["main"] = AboutMainPage(self.go_to)
        self.pages["credits"] = AboutTextPage(
            "about_credits",
            "Credits",
            MarkdownLoader.load_markdown("CREDITS.md")
        )
        self.pages["legal"] = AboutTextPage(
            "about_legal",
            "Legal",
            MarkdownLoader.load_markdown("LICENSE.md")
        )
        self.pages["whats_new"] = AboutTextPage(
            "about_whats_new",
            "What's New",
            MarkdownLoader.load_markdown("WHATSNEW.md")
        )

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.pages["main"])
        self.current_index = self.stack.currentIndex()

        close_btn = QPushButton(Traduction.get_trad("close", "Close"))
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.PANEL};
                color: {Theme.TEXT};
                border-radius: 16px;
            }}
        """)

    def show_back_button(self):
        self.back_btn.setEnabled(True)
        self.back_btn.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        anim = QPropertyAnimation(self.back_opacity, b"opacity", self)
        anim.setDuration(120)
        anim.setStartValue(self.back_opacity.opacity())
        anim.setEndValue(1.0)
        anim.start()
        self.animations.append(anim)


    def hide_back_button(self):
        self.back_btn.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        anim = QPropertyAnimation(self.back_opacity, b"opacity", self)
        anim.setDuration(120)
        anim.setStartValue(self.back_opacity.opacity())
        anim.setEndValue(0.0)

        def finish():
            self.back_btn.setEnabled(False)
        anim.finished.connect(finish)
        anim.start()
        self.animations.append(anim)



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
