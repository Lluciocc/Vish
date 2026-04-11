from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QMenu, QGraphicsView
from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF
from PySide6.QtGui import QCursor, QPen, QColor, QPainter, QBrush, QPainterPath, QLinearGradient, QFont, QKeySequence
from commands.undo_commands import *
from core.logger import Logger
from core.config import Config


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

# TODO: add options for font, opacity, etc. (maybe in a future update)

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
        self.header_height = 36
        self.resizing = False
        self.resize_corner = None
        self.locked = False
        self._hover = False
        self._accent_index = accent_index % len(ACCENT_COLORS)
        self._dragging_header = False
        self.move_children = True
        self._pin_hover = False

        self._captured_nodes = []

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

    # https://noobtomaster.com/computer-graphics/color-blending-and-color-interpolation/
    def blend_colors(self, c1: QColor, c2: QColor, ratio: float) -> QColor: # Blends two colors together by a given ratio (0.0 - 1.0)
        r = c1.red()   * (1 - ratio) + c2.red()   * ratio
        g = c1.green() * (1 - ratio) + c2.green() * ratio
        b = c1.blue()  * (1 - ratio) + c2.blue()  * ratio
        a = c1.alpha() * (1 - ratio) + c2.alpha() * ratio
        return QColor(int(r), int(g), int(b), int(a))

    def _update_title_position(self):
        self.title_item.setTextWidth(-1)
        text_rect = self.title_item.boundingRect()
        padding = 12 

        self.header_height = max(36, text_rect.height() + padding)

        y_off = (self.header_height - text_rect.height()) / 2
        self.title_item.setPos(12, y_off)

    def _on_title_changed(self):
        self.title_item.setTextWidth(-1)

        # force recalculation of bounding rect
        doc = self.title_item.document()
        doc.adjustSize()
        text_rect = self.title_item.boundingRect()
        padding = 12
        self.header_height = max(36, text_rect.height() + padding)

        y_off = (self.header_height - text_rect.height()) / 2
        self.title_item.setPos(12, y_off)

        text_w = text_rect.width()
        r = self.rect()
        min_w = max(160.0, text_w + 24)
        if r.width() < min_w:
            self.setRect(QRectF(0, 0, min_w, r.height()))

        self.update()

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
        return QRectF(r.x(), r.y(), r.width(), self.header_height).contains(pos)

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

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self._dragging_header and self.move_children:
            delta = value - self.pos()

            for node in self._captured_nodes:
                node.setPos(node.pos() + delta)
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._call_auto_save()

        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        body_path = QPainterPath()
        body_path.addRoundedRect(r, RADIUS, RADIUS)
        painter.setPen(Qt.NoPen)
        base_bg = QColor(18, 20, 28, 185)
        tinted_bg = self.blend_colors(base_bg, self.accent, 0.12)
        painter.setBrush(QBrush(tinted_bg))
        painter.drawPath(body_path)

        header_rect = QRectF(r.x(), r.y(), r.width(), self.header_height)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, RADIUS, RADIUS)
        clip = QPainterPath()
        clip.addRect(QRectF(r.x(), r.y() + RADIUS, r.width(), self.header_height - RADIUS))
        header_path = header_path.united(clip)
        painter.setBrush(QBrush(COLOR_HEADER_BG))
        painter.drawPath(header_path)

        sep_color = QColor(self.accent)
        sep_color.setAlpha(60)
        painter.setPen(QPen(sep_color, 1))
        painter.drawLine(
            QPointF(r.x() + RADIUS, r.y() + self.header_height),
            QPointF(r.right() - RADIUS, r.y() + self.header_height),
        )

        pin_size = 16
        pin_rect = QRectF(
            r.right() - 26,
            r.y() + (self.header_height - pin_size) / 2,
            pin_size,
            pin_size
        )
        self._pin_rect = pin_rect
        center = pin_rect.center()
        cx = center.x()
        cy = center.y()

        is_active = self.move_children

        pin_bg = QColor(255, 255, 255, 35 if self._pin_hover else 18)
        painter.setBrush(QBrush(pin_bg))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pin_rect, 4, 4)

        if is_active:
            icon_color = QColor(self.accent)
            icon_color.setAlpha(220)
        else:
            icon_color = QColor(160, 160, 170, 110)

        pen = QPen(icon_color, 1.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        head_rect = QRectF(cx - 3.5, cy - 6, 7, 4.5)
        painter.setBrush(QBrush(icon_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(head_rect, 2, 2)

        tip_path = QPainterPath()
        tip_path.moveTo(cx - 3, cy - 1)
        tip_path.lineTo(cx + 3, cy - 1)
        tip_path.lineTo(cx, cy + 4)
        tip_path.closeSubpath()
        painter.setBrush(QBrush(icon_color))
        painter.drawPath(tip_path)

        stem_color = QColor(icon_color)
        stem_color.setAlpha(icon_color.alpha() // 2)
        painter.setPen(QPen(stem_color, 1.1, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(cx, cy - 1.0), QPointF(cx, cy - 1.2))

        if not is_active:
            slash_color = QColor(200, 100, 100, 120)
            painter.setPen(QPen(slash_color, 1.0, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(
                QPointF(pin_rect.left() + 2.5, pin_rect.bottom() - 2.5),
                QPointF(pin_rect.right() - 2.5, pin_rect.top() + 2.5),
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
        self._pin_hover = False
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
        if hasattr(self, "_pin_rect") and self._pin_rect.contains(event.pos()):
            self._pin_hover = True
            self.setCursor(Qt.PointingHandCursor)
            self.update()
        elif corner:
            self._pin_hover = False
            self.setCursor(cursors[corner])
        elif self._in_header(event.pos()):
            self._pin_hover = False
            self.setCursor(Qt.OpenHandCursor)
        else:
            self._pin_hover = False
            self.setCursor(Qt.ArrowCursor)
        self.update()
        super().hoverMoveEvent(event)

    def contextMenuEvent(self, event):
        if not self._in_header(event.pos()):
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                
                view.setDragMode(QGraphicsView.NoDrag)
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
        try:
            if action == lock_action:
                self.set_locked(not self.locked)
            elif action in color_actions:
                self.set_accent(color_actions.index(action))
            elif action == delete_action:
                self._delete_self()
        finally: # always call graph_changed after context menu actions
            self._call_auto_save()
    
        event.accept()

    def _call_auto_save(self):
        if self.scene() and self.scene().views() and Config.AUTO_SAVE:
            view = self.scene().views()[0]
            view.graph_scene.auto_save_triggered.emit()

    def mousePressEvent(self, event):
        if self.locked:
            event.ignore()
            return

        if hasattr(self, "_pin_rect") and self._pin_rect.contains(event.pos()):
            self.move_children = not self.move_children
            self.update()
            self._call_auto_save()

            self.setCursor(Qt.PointingHandCursor)
            event.accept()
            return
        else:
            if self._pin_hover:
                self._pin_hover = False
                self.update()

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

            if self.move_children:
                self._capture_nodes()

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
        self._call_auto_save()

    def mouseReleaseEvent(self, event):
        self._captured_nodes = []
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
            Logger.LogMessage("Comment box deleted")

    def _capture_nodes(self):
        self._captured_nodes = []

        if not self.scene():
            return

        from ui.node_item import NodeItem

        rect = self.sceneBoundingRect()

        for item in self.scene().items():
            if isinstance(item, NodeItem):
                center = item.sceneBoundingRect().center()

                if rect.contains(center):
                    self._captured_nodes.append(item)
