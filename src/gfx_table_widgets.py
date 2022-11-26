# 1. std
import math
from typing import Tuple
# 2. 3rd
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPolygonF, QPainterPath, QPen, QResizeEvent, QColor, QFont, QPalette
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, \
    QFrame, QGraphicsSimpleTextItem, QLabel

# x. const
DataValue = Tuple[str, int, QColor]
POINTS = 12
FONT_MAIN = QFont('mono', 8)


def mk_sin(o: int = 0) -> list[float]:
    """
    Make sinusoide graph coordinates. Y=0..1
    :param o: Offset, points
    :return: list of y (0..1)
    """
    return [(1 + math.sin((i + o) * 2 * math.pi / POINTS)) / 2 for i in range(POINTS + 1)]


class TextItem(QGraphicsSimpleTextItem):
    """
    - [x] TODO: disable scaling
    - [x] TODO: color
    - [ ] TODO: disable v-resize
    Warn: on resize:
    - not changed: boundingRect(), pos(), scenePos()
    - not call: deviceTransform(), itemTransform(), transform(), boundingRegion()
    - call: paint()
    """
    def __init__(self, txt: str, color: QColor = None):
        super().__init__(txt)
        self.setFont(FONT_MAIN)
        if color:
            self.setBrush(color)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)


class TextWidget(QLabel):
    def __init__(self, txt: str, color: QColor = None, parent=None):
        super().__init__(txt, parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # transparent bg
        self.setFont(FONT_MAIN)
        if color:
            p = QPalette()
            p.setColor(QPalette.WindowText, color)
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
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
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
    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        pg = QPolygonF([QPointF(x * 10, y * 10) for x, y in enumerate(mk_sin(d[1]))])
        pp = QPainterPath()
        pp.addPolygon(pg)
        self.setPath(pp)
        pen = QPen(d[2])
        pen.setCosmetic(True)  # !!! don't resize pen width
        self.setPen(pen)


class GraphView(QGraphicsView):  # <= QAbstractScrollArea <= QFrame
    def __init__(self, d: DataValue):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.scene().addItem(GraphItem(d))

    def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
        # super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.IgnoreAspectRatio)  # expand to max
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
        w.setFrameShape(QFrame.HLine)
        w.setLineWidth(0)


class VLineGfxWidget(QGraphicsProxyWidget):
    def __init__(self):
        super().__init__()
        self.setWidget(w := QFrame())
        w.setFrameShape(QFrame.VLine)
        w.setLineWidth(0)
