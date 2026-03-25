from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QMenu
from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF
from PySide6.QtGui import QPen, QColor, QPainter, QBrush, QPainterPath, QLinearGradient, QFont, QKeySequence
from commands.undo_commands import *
from core.logger import Logger


ACCENT_COLORS = [
    QColor(99, 179, 237),   # sky blue
    QColor(154, 117, 242),  # violet
    QColor(72, 199, 142),   # mint
    QColor(250, 176, 5),    # amber
    QColor(240, 101, 101),  # coral
]

COLOR_BG = QColor(18, 20, 28, 185)         # dark body background
COLOR_HEADER_BG = QColor(255, 255, 255, 12) # subtle header tint
COLOR_BORDER = QColor(255, 255, 255, 30)    # default border
COLOR_BORDER_SEL = QColor(255, 255, 255, 90) # selected border
COLOR_TITLE = QColor(230, 230, 240)         # title text

RADIUS = 10
HEADER_H = 36

# TODO: add options for font, opacity, etc. (maybe in a future update)
# TODO: Fix Z order
# TODO: Move node inside comment box when dragging the box
# TODO: Custom colors
# TODO: Works with Config.AUTO_SAVE

class CommentBoxItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF = QRectF(0, 0, 320, 200), title: str = "Comment", accent_index: int = 0):
        super().__init__(rect)

        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setZValue(-10_000)

        self.resize_margin = 12
        self.resizing = False
        self.resize_corner = None
        self.locked = False
        self._hover = False
        self._accent_index = accent_index % len(ACCENT_COLORS)
        self._dragging_header = False

        self.setPen(Qt.NoPen)
        self.setBrush(Qt.NoBrush)

        self.title_item = QGraphicsTextItem(title, self)
        font = QFont("Segoe UI", 10, QFont.Medium)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 0.3)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(COLOR_TITLE)
        self.title_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.title_item.setFlag(QGraphicsItem.ItemIsFocusable)
        self.title_item.setAcceptedMouseButtons(Qt.LeftButton)
        self.title_item.document().contentsChanged.connect(self._on_title_changed)

        self._update_title_position()

    @property
    def accent(self) -> QColor:
        return ACCENT_COLORS[self._accent_index]

    def _update_title_position(self):
        self.title_item.setTextWidth(-1)
        fm_h = self.title_item.boundingRect().height()
        y_off = (HEADER_H - fm_h) / 2
        self.title_item.setPos(12, y_off)

    def _on_title_changed(self):
        self.title_item.setTextWidth(-1)
        text_w = self.title_item.boundingRect().width()
        r = self.rect()
        min_w = max(160.0, text_w + 24)
        if r.width() < min_w:
            self.setRect(QRectF(0, 0, min_w, r.height()))

    def _get_resize_corner(self, pos: QPointF) -> str | None:
        r = self.rect()
        m = self.resize_margin
        corners = {
            "tl": QRectF(r.topLeft(), QSizeF(m, m)),
            "tr": QRectF(r.topRight() - QPointF(m, 0), QSizeF(m, m)),
            "bl": QRectF(r.bottomLeft() - QPointF(0, m), QSizeF(m, m)),
            "br": QRectF(r.bottomRight() - QPointF(m, m), QSizeF(m, m)),
        }
        for name, zone in corners.items():
            if zone.contains(pos):
                return name
        return None

    def _in_header(self, pos: QPointF) -> bool:
        r = self.rect()
        return QRectF(r.x(), r.y(), r.width(), HEADER_H).contains(pos)

    def _delete_self(self):
        if self.scene():
            self.scene().removeItem(self)

    def set_locked(self, locked: bool):
        self.locked = locked
        self.setAcceptHoverEvents(not locked)
        if locked:
            self.title_item.setTextInteractionFlags(Qt.NoTextInteraction)
            self.setCursor(Qt.ArrowCursor)
        else:
            self.title_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.update()

    def set_accent(self, index: int):
        self._accent_index = index % len(ACCENT_COLORS)
        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        body_path = QPainterPath()
        body_path.addRoundedRect(r, RADIUS, RADIUS)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(COLOR_BG))
        painter.drawPath(body_path)

        header_rect = QRectF(r.x(), r.y(), r.width(), HEADER_H)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, RADIUS, RADIUS)
        clip = QPainterPath()
        clip.addRect(QRectF(r.x(), r.y() + RADIUS, r.width(), HEADER_H - RADIUS))
        header_path = header_path.united(clip)
        painter.setBrush(QBrush(COLOR_HEADER_BG))
        painter.drawPath(header_path)

        sep_color = QColor(self.accent)
        sep_color.setAlpha(60)
        painter.setPen(QPen(sep_color, 1))
        painter.drawLine(
            QPointF(r.x() + RADIUS, r.y() + HEADER_H),
            QPointF(r.right() - RADIUS, r.y() + HEADER_H),
        )

        a = self.accent
        transparent = QColor(a.red(), a.green(), a.blue(), 0)
        stripe = QLinearGradient(r.x(), 0, r.right(), 0)
        stripe.setColorAt(0.0, transparent)
        stripe.setColorAt(0.35, a)
        stripe.setColorAt(0.65, a)
        stripe.setColorAt(1.0, transparent)
        stripe_path = QPainterPath()
        stripe_path.addRoundedRect(QRectF(r.x(), r.y(), r.width(), 2.5), 1.5, 1.5)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(stripe))
        painter.drawPath(stripe_path)

        if self.locked:
            lock_color = QColor(self.accent)
            lock_color.setAlpha(130)
            painter.setPen(QPen(lock_color, 1.2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(body_path)
        else:
            if self.isSelected():
                border_color = COLOR_BORDER_SEL
            elif self._hover:
                border_color = QColor(255, 255, 255, 55)
            else:
                border_color = COLOR_BORDER
            painter.setPen(QPen(border_color, 1.0))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(body_path)

    def hoverEnterEvent(self, event):
        self._hover = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hover = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        corner = self._get_resize_corner(event.pos())
        cursors = {
            "tl": Qt.SizeFDiagCursor,
            "br": Qt.SizeFDiagCursor,
            "tr": Qt.SizeBDiagCursor,
            "bl": Qt.SizeBDiagCursor,
        }
        if corner:
            self.setCursor(cursors[corner])
        elif self._in_header(event.pos()):
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def contextMenuEvent(self, event):
        if not self._in_header(event.pos()):
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]

                scene_pos = event.scenePos()
                view.show_node_palette(scene_pos)

            event.accept()
            return

        menu = QMenu()
        lock_action = menu.addAction("Unlock" if self.locked else "Lock")
        menu.addSeparator()
        color_menu = menu.addMenu("Accent colour")
        color_names = ["Blue", "Violet", "Green", "Yellow", "Red"]
        color_actions = [
            color_menu.addAction(f"{'●' if i == self._accent_index else '○'} {n}")
            for i, n in enumerate(color_names)
        ]
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        action = menu.exec(event.screenPos())
        if action == lock_action:
            self.set_locked(not self.locked)
        elif action in color_actions:
            self.set_accent(color_actions.index(action))
        elif action == delete_action:
            self._delete_self()
        event.accept()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Delete):
            self._delete_self()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self.locked:
            event.ignore()
            return

        corner = self._get_resize_corner(event.pos())
        in_header = self._in_header(event.pos())

        if not corner and not in_header and not self.title_item.isUnderMouse():
            event.ignore()
            return

        self.resize_corner = corner
        self.resizing = corner is not None

        self.drag_start_pos = event.screenPos()
        self.original_rect = QRectF(self.rect())
        self.original_item_pos = self.pos()

        if in_header and not self.resizing:
            self._dragging_header = True
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setCursor(Qt.ClosedHandCursor)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.resizing:
            super().mouseMoveEvent(event)
            return

        min_w = 160
        min_h = 80
        delta = event.screenPos() - self.drag_start_pos
        orig = self.original_rect
        orig_pos = self.original_item_pos

        if self.resize_corner == "br":
            w = max(min_w, orig.width() + delta.x())
            h = max(min_h, orig.height() + delta.y())
            self.setRect(QRectF(0, 0, w, h))
        elif self.resize_corner == "tr":
            w = max(min_w, orig.width() + delta.x())
            h = max(min_h, orig.height() - delta.y())
            self.setPos(orig_pos.x(), orig_pos.y() + orig.height() - h)
            self.setRect(QRectF(0, 0, w, h))
        elif self.resize_corner == "bl":
            w = max(min_w, orig.width() - delta.x())
            h = max(min_h, orig.height() + delta.y())
            self.setPos(orig_pos.x() + orig.width() - w, orig_pos.y())
            self.setRect(QRectF(0, 0, w, h))
        elif self.resize_corner == "tl":
            w = max(min_w, orig.width() - delta.x())
            h = max(min_h, orig.height() - delta.y())
            self.setPos(orig_pos.x() + orig.width() - w, orig_pos.y() + orig.height() - h)
            self.setRect(QRectF(0, 0, w, h))

        self._update_title_position()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None
        self._dragging_header = False
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        if self._hover:
            pos = event.pos()
            self.setCursor(Qt.OpenHandCursor if self._in_header(pos) else Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def setRect(self, rect: QRectF):
        super().setRect(rect)
        self._update_title_position()

    def _delete_self(self):
        if self.scene() and self.scene().views():
            view = self.scene().views()[0]
            if hasattr(view, "undo_stack"):
                view.undo_stack.push(RemoveCommentCommand(view, self))