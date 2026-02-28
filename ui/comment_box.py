from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu
from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF
from PySide6.QtGui import QPen, QColor


class CommentBoxItem(QGraphicsRectItem):
    def __init__(self, rect=QRectF(0, 0, 300, 200), title="Comment"):
        super().__init__(rect)

        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable
        )

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable)
        self.setZValue(-10000)  # Ensure it's behind all nodes and edges

        self.resize_margin = 10
        self.title_bar_height = 32
        self.resizing = False
        self.resize_corner = None
        self.locked = False

        pen = QPen(QColor(220, 220, 220))
        pen.setWidth(2)
        self.setPen(pen)
        self.setBrush(QColor(255, 255, 255, 40))

        self.title_item = QGraphicsTextItem(title, self)
        self.title_item.setDefaultTextColor(QColor(240, 240, 240))

        self.title_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.title_item.setFlag(QGraphicsTextItem.ItemIsFocusable)
        self.title_item.setAcceptedMouseButtons(Qt.LeftButton)

        self.title_padding = 8
        self._update_title_position()

    def _update_title_position(self):
        r = self.rect()

        width = r.width() * 0.9
        self.title_item.setTextWidth(width)

        self.title_item.setPos(
            (r.width() - width) * 0.5,
            self.title_padding
        )



    def _get_resize_corner(self, pos: QPointF):
        r = self.rect()
        m = self.resize_margin

        if QRectF(r.topLeft(), QSizeF(m, m)).contains(pos):
            return "tl"
        if QRectF(r.topRight() - QPointF(m, 0), QSizeF(m, m)).contains(pos):
            return "tr"
        if QRectF(r.bottomLeft() - QPointF(0, m), QSizeF(m, m)).contains(pos):
            return "bl"
        if QRectF(r.bottomRight() - QPointF(m, m), QSizeF(m, m)).contains(pos):
            return "br"
        return None
    
    def set_locked(self, locked: bool):
        self.locked = locked

        self.setFlag(QGraphicsRectItem.ItemIsMovable, not locked)
        self.setAcceptHoverEvents(not locked)
        self.setCursor(Qt.ArrowCursor if locked else Qt.OpenHandCursor)

        if locked:
            self.setBrush(QColor(255, 255, 255, 20))
            self.title_item.setTextInteractionFlags(Qt.NoTextInteraction)
        else:
            self.setBrush(QColor(255, 255, 255, 40))
            self.title_item.setTextInteractionFlags(Qt.TextEditorInteraction)

        self.update()

    def contextMenuEvent(self, event):
        menu = QMenu()

        lock_action = menu.addAction("Unlock" if self.locked else "Lock")

        action = menu.exec(event.screenPos())
        if action == lock_action:
            self.set_locked(not self.locked)
        event.accept()



    def hoverMoveEvent(self, event):
        corner = self._get_resize_corner(event.pos())
        if corner:
            match corner:
                case "tl":
                    self.setCursor(Qt.SizeFDiagCursor)
                case "tr":
                    self.setCursor(Qt.SizeBDiagCursor)
                case "bl":
                    self.setCursor(Qt.SizeBDiagCursor)
                case "br":
                    self.setCursor(Qt.SizeFDiagCursor)
                case _:
                    self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.locked:
            super().mousePressEvent(event)
            return
        if self.title_item.isUnderMouse():
            event.accept()
            return

        self.resize_corner = self._get_resize_corner(event.pos())
        self.resizing = self.resize_corner is not None
        self.drag_start_pos = event.pos()
        self.original_rect = QRectF(self.rect())
        self.original_item_pos = self.pos()
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if not self.resizing:
            super().mouseMoveEvent(event)
            return

        min_w, min_h = 120, 60
        delta = event.pos() - self.drag_start_pos

        orig = self.original_rect
        orig_pos = self.original_item_pos

        if self.resize_corner == "br":
            w = max(min_w, orig.width() + delta.x())
            h = max(min_h, orig.height() + delta.y())
            self.setRect(QRectF(0, 0, w, h))

        elif self.resize_corner == "tr":
            w = max(min_w, orig.width() + delta.x())
            h = max(min_h, orig.height() - delta.y())
            self.setPos(orig_pos.x(), orig_pos.y() + (orig.height() - h))
            self.setRect(QRectF(0, 0, w, h))

        elif self.resize_corner == "bl":
            w = max(min_w, orig.width() - delta.x())
            h = max(min_h, orig.height() + delta.y())
            self.setPos(orig_pos.x() + (orig.width() - w), orig_pos.y())
            self.setRect(QRectF(0, 0, w, h))

        elif self.resize_corner == "tl":
            w = max(min_w, orig.width() - delta.x())
            h = max(min_h, orig.height() - delta.y())
            self.setPos(orig_pos.x() + (orig.width() - w), orig_pos.y() + (orig.height() - h))
            self.setRect(QRectF(0, 0, w, h))

        self._update_title_position()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None
        super().mouseReleaseEvent(event)

    def setRect(self, rect: QRectF):
        super().setRect(rect)
        self._update_title_position()

