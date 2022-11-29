# 1. std
from typing import Union, List
import math
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRect, QRectF, QSize, QSizeF
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QPainter
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, \
    QWidget, QStyleOptionGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLayoutItem
# 3. local
from gfx_ppreview_const import FONT_MAIN, DataValue, POINTS, W_LABEL, DEBUG, HEADER_TXT


def qsize2str(size: Union[QRect, QRectF, QSize, QSizeF]) -> str:
    if isinstance(size, QRectF):
        v = size.size().toSize()
    elif isinstance(size, QRect):
        v = size.size()
    elif isinstance(size, QSizeF):
        v = size.toSize()
    else:
        v = size
    return f"({v.width()}, {v.height()})"


def mk_sin(o: int = 0) -> list[float]:
    """
    Make sinusoide graph coordinates. Y=0..1
    :param o: Offset, points
    :return: list of y (0..1)
    """
    return [(1 + math.sin((i + o) * 2 * math.pi / POINTS)) / 2 for i in range(POINTS + 1)]


# ---- QGraphicsItem ----
class TextItem(QGraphicsSimpleTextItem):
    """
    Warn: on resize:
    - not changed: boundingRect(), pos(), scenePos()
    - not call: deviceTransform(), itemTransform(), transform(), boundingRegion()
    - call: paint()
    """
    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__(txt)
        self.bordered = False
        self.setFont(FONT_MAIN)
        if color:
            self.setBrush(color)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        # print(qsize2str(self.boundingRect()))


class RectTextItem(QGraphicsItemGroup):
    """Text in border.
    Result: something strange."""
    text: TextItem
    rect: QGraphicsRectItem

    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__()
        # text
        self.text = TextItem(txt, color)
        self.addToGroup(self.text)
        # rect
        self.rect = QGraphicsRectItem(self.text.boundingRect())  # default size == text size
        self.addToGroup(self.rect)
        if DEBUG:
            pen = QPen(color or Qt.GlobalColor.black)
            pen.setCosmetic(True)
        else:
            pen = QPen(Qt.GlobalColor.transparent)
        self.rect.setPen(pen)
        # clip label
        self.rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # YES!!!
        self.text.setParentItem(self.rect)

    def set_width(self, w: float):
        r = self.rect.rect()
        r.setWidth(w)
        self.rect.setRect(r)

    def set_height(self, h: float):
        r = self.rect.rect()
        r.setHeight(h)
        self.rect.setRect(r)

    def set_size(self, s: QSizeF):  # self.rect.rect() = self.rect.boundingRect() + 1
        self.prepareGeometryChange()  # not helps
        r = self.rect.rect()
        r.setWidth(s.width())
        r.setHeight(s.height())
        self.rect.setRect(r)


class GraphItem(QGraphicsPathItem):
    __y: List[float]

    def __init__(self, d: DataValue):
        super().__init__()
        self.__y = mk_sin(d[1])
        pen = QPen(d[2])
        pen.setCosmetic(True)
        self.setPen(pen)
        pp = QPainterPath()
        pp.addPolygon(QPolygonF([QPointF(x, y) for x, y in enumerate(self.__y)]))  # default
        self.setPath(pp)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """For debug only"""
        super().paint(painter, option, widget)
        if DEBUG:
            painter.setPen(self.pen())
            painter.drawRect(option.rect)

    def set_size(self, s: QSizeF):
        """

        :param s: Size of graph
        :return:
        """
        self.prepareGeometryChange()  # not helps
        pp = self.path()
        step = s.width() / (pp.elementCount() - 1)
        for i in range(pp.elementCount()):
            pp.setElementPositionAt(i, i * step, self.__y[i] * s.height())
        self.setPath(pp)


# ---- QGraphicsView
class GraphViewBase(QGraphicsView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
        # super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max
        # Note: KeepAspectRatioByExpanding is extremally CPU-greedy


class GraphView(GraphViewBase):  # <= QAbstractScrollArea <= QFrame
    def __init__(self, d: DataValue):
        super().__init__()
        self.scene().addItem(GraphItem(d))


# ---- Helpers
class HeaderItem(RectTextItem):
    __plot: 'Plot'

    def __init__(self, plot: 'Plot'):
        super().__init__(HEADER_TXT)
        self.__plot = plot
        self.update_size()

    def update_size(self):
        self.set_width(self.__plot.w_full)


class RowItem(QGraphicsItemGroup):
    __plot: 'Plot'
    __label: RectTextItem
    __wide: bool
    __graph: GraphItem

    def __init__(self, d: DataValue, plot: 'Plot'):
        super().__init__()
        self.__plot = plot
        self.__label = RectTextItem(d[0], d[2])
        self.__graph = GraphItem(d)
        self.__wide = d[3]
        self.__label.set_width(W_LABEL)
        self.__graph.setX(W_LABEL + 1)
        self.update_size()
        self.addToGroup(self.__label)
        self.addToGroup(self.__graph)

    def update_size(self):
        w = self.__plot.w_full - W_LABEL  # 1077, 695
        h = self.__plot.h_row_base * (1 + int(self.__wide) * 3)  # 28/112, 42/168
        # print(f"W={w}, H={h}")
        self.__label.set_height(h)
        self.__graph.set_size(QSizeF(w, h))


# TODO: class BottomItem(rect+(rect(txt))

class LayoutItem(QGraphicsLayoutItem):
    """QGraphicsLayoutItem(QGraphicsItem) based."""
    __subj: QGraphicsItem  # must live

    def __init__(self, subj: QGraphicsItem):
        super().__init__()
        self.__subj = subj
        self.setGraphicsItem(self.__subj)
        # experiments:
        # self.__subj.setFlag(QGraphicsItem.ItemClipsToShape, True)
        # self.__subjsetFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
        # self.__subj.setFlag(QGraphicsItem.ItemContainsChildrenInShape)
        # self.setMinimumHeight(self.__subj.boundingRect().height())
        # self.setPreferredHeight(self.__subj.boundingRect().height())
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)  # ✗

    def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
        if which in {Qt.SizeHint.MinimumSize, Qt.SizeHint.PreferredSize}:
            return self.graphicsItem().boundingRect().size()
        return constraint

    def setGeometry(self, rect: QRectF):  # Warn: Calling once on init
        self.graphicsItem().prepareGeometryChange()
        super().setGeometry(rect)
        self.graphicsItem().setPos(rect.topLeft())
