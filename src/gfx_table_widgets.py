# 1. std
from typing import Tuple, Union
import math
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRect, QRectF, QSize, QSizeF
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QFont, QPainter
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsSimpleTextItem, \
    QWidget, QStyleOptionGraphicsItem, QGraphicsRectItem, \
    QGraphicsItemGroup, QGraphicsLayoutItem, QSizePolicy

# x. const
PPP = 5  # plots per page
FONT_MAIN = QFont('mono', 8)
DataValue = Tuple[str, int, Qt.GlobalColor]
POINTS = 12
W_LABEL = 64  # width of label column
W_GRAPH_STEP = W_LABEL // 4
H_GRAPH = 14  # bigger makes label b-cutted
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line."
DATA = (  # name, x-offset, color
    ("Signal 1", 0, Qt.GlobalColor.black),
    ("Signal 22", 1, Qt.GlobalColor.red),
    ("Signal 3333", 2, Qt.GlobalColor.blue),
    ("Signal 4", 3, Qt.GlobalColor.green),
    ("Signal 5", 4, Qt.GlobalColor.yellow),
    ("Signal 6", 5, Qt.GlobalColor.magenta),
)


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
    bordered: bool

    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__(txt)
        self.bordered = False
        self.setFont(FONT_MAIN)
        if color:
            self.setBrush(color)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

    '''
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """Notes:
        - widget is not None
        - painter.clipBoundingRect() = 0, 0
        - option.rect == self.boundingRect()
        """
        super().paint(painter, option, widget)
        if self.bordered:
            pen = QPen()
            pen.setCosmetic(True)
            # item border
            pen.setColor(Qt.GlobalColor.black)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())
            # place border (more precise)
            pen.setColor(Qt.GlobalColor.blue)
            painter.setPen(pen)
            painter.drawRect(option.rect)
    '''


class RectTextItem(QGraphicsItemGroup):
    """Text in border.
    Result: something strange."""
    bordered: bool
    text: TextItem
    rect: QGraphicsRectItem

    def __init__(self, width: int, txt: str, color: Qt.GlobalColor = None):
        super().__init__()
        # text
        self.text = TextItem(txt, color)
        self.addToGroup(self.text)
        # rect
        r = self.text.boundingRect()
        r.setWidth(width)
        self.rect = QGraphicsRectItem(r)
        if color:
            pen = QPen(color)
            pen.setCosmetic(True)
            self.rect.setPen(pen)
        self.addToGroup(self.rect)
        # clip label
        self.rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # YES!!!
        self.text.setParentItem(self.rect)


class GraphItem(QGraphicsPathItem):
    bordered: bool

    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.bordered = False
        # W: ..., H: 1xChar
        pg = QPolygonF([QPointF(x * W_GRAPH_STEP, y * H_GRAPH) for x, y in enumerate(mk_sin(d[1]))])
        pp = QPainterPath()
        pp.addPolygon(pg)
        self.setPath(pp)
        pen = QPen(d[2])
        pen.setCosmetic(True)  # !!! don't resize pen width
        self.setPen(pen)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        super().paint(painter, option, widget)
        if self.bordered:
            painter.setPen(self.pen())
            painter.drawRect(option.rect)


# ---- QGraphicsView
class GraphView(QGraphicsView):  # <= QAbstractScrollArea <= QFrame
    def __init__(self, d: DataValue):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.scene().addItem(GraphItem(d))

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
        # super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max
        # Note: KeepAspectRatioByExpanding is extremally CPU-greedy


# ---- Helpers
class RowItem(QGraphicsItemGroup):
    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.addToGroup(RectTextItem(W_LABEL - 1, d[0], d[2]))
        self.addToGroup(graph := GraphItem(d))
        graph.setX(W_LABEL)
        graph.bordered = True


class LayoutItem(QGraphicsLayoutItem):
    """QGraphicsLayoutItem(QGraphicsItem) based."""
    __subj: QGraphicsItem  # must live

    def __init__(self, subj: QGraphicsItem):
        super().__init__()
        self.__subj = subj
        self.setGraphicsItem(self.__subj)
        # experiments:
        self.__subj.bordered = True
        # self.__subj.setFlag(QGraphicsItem.ItemClipsToShape, True)
        # self.__subjsetFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
        # self.__subj.setFlag(QGraphicsItem.ItemContainsChildrenInShape)
        # self.setMinimumHeight(self.__subj.boundingRect().height())
        # self.setPreferredHeight(self.__subj.boundingRect().height())
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)  # ✗

    def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
        if which in {Qt.SizeHint.MinimumSize, Qt.SizeHint.PreferredSize}:
            return self.__subj.boundingRect().size()
        return constraint

    def setGeometry(self, rect: QRectF):  # Warn: Calling once on init
        self.__subj.prepareGeometryChange()
        super().setGeometry(rect)
        self.__subj.setPos(rect.topLeft())
