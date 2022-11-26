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


class TextWidget(QLabel):
    def __init__(self, txt: str, color: QColor = None, parent=None):
        super().__init__(txt, parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # transparent bg
        self.setFont(FONT_MAIN)
        if color:
            # plan A
            p = QPalette()
            p.setColor(QPalette.WindowText, color)
            self.setPalette(p)
            # plan B
            # w.setStyleSheet("color: red")  # not works


class TextItem(QGraphicsSimpleTextItem):
    """
    - [x] TODO: disable scaling
    - [ ] TODO: disable v-resize
    - [ ] TODO: color
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
