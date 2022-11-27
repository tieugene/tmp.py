# 1. std
import math
from typing import Tuple, Union
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt, QRect, QRectF, QSize, QSizeF
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QColor, QFont, QPalette, QPainter
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, \
    QFrame, QGraphicsSimpleTextItem, QLabel, QWidget, QStyleOptionGraphicsItem, QGraphicsWidget, QGraphicsRectItem, \
    QGraphicsItemGroup

# x. const
DataValue = Tuple[str, int, Qt.GlobalColor]
POINTS = 12
FONT_MAIN = QFont('mono', 8)


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


class RectTextItem(QGraphicsItemGroup):
    """Text in border.
    Result: something strange."""
    bordered: bool
    rect: QGraphicsRectItem
    text: QGraphicsSimpleTextItem

    def __init__(self, txt: str, color: Qt.GlobalColor = None):
        super().__init__()
        # text
        self.text = QGraphicsSimpleTextItem(txt)
        self.text.setFont(FONT_MAIN)
        self.text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        # rect
        self.rect = QGraphicsRectItem(self.text.boundingRect())
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)  # YES!!!
        # color up
        if color:
            self.text.setBrush(color)
            pen = QPen(color)
            pen.setCosmetic(True)
            self.rect.setPen(pen)
        # altogether
        self.text.setParentItem(self)
        self.addToGroup(self.rect)
        self.addToGroup(self.text)


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


class TextWidget(QLabel):
    def __init__(self, txt: str, color: QColor = None, parent=None):
        super().__init__(txt, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)  # transparent bg
        self.setFont(FONT_MAIN)
        if color:
            p = QPalette()
            p.setColor(QPalette.ColorRole.WindowText, color)
            self.setPalette(p)
        # self.setStyleSheet("border: 1px solid black")  # not works


class TextGfxWidget(QGraphicsProxyWidget):  # <= QGraphicsWidget
    """QGraphicsProxyWidget(QWidget) based.
    Not good:
    - [+] color
    - [?] v-align: center?
    - [-] v-size: strange
    - [+] cut
    - [-] no border
    """
    __vcentered: bool

    def __init__(self, txt: str, color: QColor = None, vcentered: bool = False):
        # Signal x: (53, 14)
        super().__init__()
        self.__vcentered = vcentered
        self.setWidget(TextWidget(txt, color))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        # print(f"{txt}: label={qsize2str(self.widget().size())}, self={qsize2str(self.boundingRect().size())}")

    '''
    def boundingRect(self) -> QRectF:
        # return super().boundingRect().adjusted(0, 0, 0, 0)  # too big (54, 96)
        return QRectF(0, 0, (s := self.widget().size()).width(), s.height())

    def paintWindowFrame(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...):
        """Not calling.
        RTFM examples/../embeddeddialogs
        """
        print("Go!")
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)
        painter.drawRect(self.windowFrameRect())
        super().paintWindowFrame(painter, option, widget)
    '''


class GraphItem(QGraphicsPathItem):
    bordered: bool

    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.bordered = False
        pg = QPolygonF([QPointF(x * 50, y * 14) for x, y in enumerate(mk_sin(d[1]))])
        pp = QPainterPath()
        pp.addPolygon(pg)
        self.setPath(pp)
        pen = QPen(d[2])
        pen.setCosmetic(True)  # !!! don't resize pen width
        self.setPen(pen)
        # self.setFlag(QGraphicsItem.ItemIgnoresTransformations, False)  # ✗

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        """Note:
        - painter.setBrush(Qt.GlobalColor.white): clean bg (label cut "plan B")
        """
        if self.bordered:
            # item border
            # pen.setColor(Qt.GlobalColor.black)
            # painter.setPen(pen)
            # painter.drawRect(self.boundingRect())
            # place border (more precise)
            pen = QPen(Qt.GlobalColor.blue)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawRect(option.rect)
        super().paint(painter, option, widget)


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


class HLineGfxWidget(QGraphicsProxyWidget):
    def __init__(self):
        """Defaults:
        - lineWidth() = 1
        - frameShadow() = 16 (plain)
        - frameWidth() = 1
        - frameStyle() = 20
        """
        super().__init__()
        self.setWidget(w := QFrame())
        w.setFrameShape(QFrame.Shape.HLine)
        w.setLineWidth(0)


class VLineGfxWidget(QGraphicsProxyWidget):
    def __init__(self):
        super().__init__()
        self.setWidget(w := QFrame())
        w.setFrameShape(QFrame.Shape.VLine)
        w.setLineWidth(0)


class GraphItemGfxWidget(QGraphicsWidget):  # QGraphicsObject + QGraphicsLayoutItem
    """QGraphicsWidget(QGraphicsItem).
    == GridGraphItem + minimal sizeHint()/setGeometry()
    - [+] Lite, Simple
    - [-] Paints from screen (0, 0)
    """
    __subj: GraphItem  # must alive

    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.__subj = GraphItem(d)
        self.setGraphicsItem(self.__subj)
        # self.__subj.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

    def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
        # if which in {Qt.MinimumSize, Qt.PreferredSize}:
        #    return QSizeF(50, 20)
        return constraint

    def setGeometry(self, rect: QRectF):  # Fix painting from screen(0,0); Warn: Calling once on init
        # print("Graph setG:", qsize2str(rect))
        self.__subj.prepareGeometryChange()
        super().setGeometry(rect)
        self.__subj.setPos(rect.topLeft())
