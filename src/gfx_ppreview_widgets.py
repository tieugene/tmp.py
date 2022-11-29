# 1. std
from typing import Union
import math
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRect, QRectF, QSize, QSizeF
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QPainter
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, \
    QWidget, QStyleOptionGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, QGraphicsLayoutItem
# 3. local
from gfx_ppreview_const import FONT_MAIN, DataValue, POINTS, W_LABEL, W_GRAPH_STEP, H_GRAPH, DEBUG, HEADER_TXT


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

    def __init__(self, txt: str, width: int, color: Qt.GlobalColor = None):
        super().__init__()
        # text
        self.text = TextItem(txt, color)
        self.addToGroup(self.text)
        # rect
        r = self.text.boundingRect()
        r.setWidth(width)
        self.rect = QGraphicsRectItem(r)  # FIXME: default size == text_height x const
        if color:
            pen = QPen(color if DEBUG else Qt.GlobalColor.transparent)
            pen.setCosmetic(True)
            self.rect.setPen(pen)
        self.addToGroup(self.rect)
        # clip label
        self.rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # YES!!!
        self.text.setParentItem(self.rect)

    def set_width(self, w: float):
        ...  # TODO:

    def set_height(self, h: float):
        ...  # TODO:

    def set_size(self, s: QSizeF):
        ...  # TODO:


class GraphItem(QGraphicsPathItem):
    def __init__(self, d: DataValue):
        super().__init__()
        # W: ..., H: 1xChar
        pg = QPolygonF([QPointF(x * W_GRAPH_STEP, y * H_GRAPH) for x, y in enumerate(mk_sin(d[1]))])
        pp = QPainterPath()
        pp.addPolygon(pg)
        self.setPath(pp)
        pen = QPen(d[2])
        pen.setCosmetic(True)  # !!! don't resize pen width
        self.setPen(pen)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """For debug only"""
        super().paint(painter, option, widget)
        if DEBUG:
            painter.setPen(self.pen())
            painter.drawRect(option.rect)

    def set_size(self, s: QSizeF):
        """

        :param s: Size of row (full width x basic height)
        :return:
        """
        ...  # TODO:


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
class HeaderItem(TextItem):
    def __init__(self, plot: QGraphicsView):
        super().__init__(HEADER_TXT)
        self.__plot = plot

    def update_size(self):
        ...  # TODO:


class RowItem(QGraphicsItemGroup):
    __plot: QGraphicsView
    __label: RectTextItem
    __graph: GraphItem

    def __init__(self, d: DataValue, plot: QGraphicsView):
        super().__init__()
        self.__plot = plot
        self.__label = RectTextItem(d[0], W_LABEL, d[2])
        self.__graph = GraphItem(d)
        self.__graph.setX(W_LABEL + 1)
        self.addToGroup(self.__label)
        self.addToGroup(self.__graph)

    def update_size(self):
        ...  # TODO:


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
