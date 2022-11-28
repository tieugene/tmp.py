"""Trash can"""
from PyQt5.QtCore import Qt, QSizeF, QRectF
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QLabel, QGraphicsProxyWidget, QGraphicsItem, QFrame, QGraphicsWidget

from src.gfx_table_widgets import FONT_MAIN, DataValue, GraphView, GraphItem


def color2style(c: QColor) -> str:
    """Convert QColor into stylesheet-compatible string"""
    return "rgb(%d, %d, %d)" % (c.red(), c.green(), c.blue())


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


class GraphViewGfxWidget(QGraphicsProxyWidget):  # <= QGraphicsWidget
    """QGraphicsProxyWidget(QGraphicsView).
    - [+] OK
    - [?] not transparent
    - [-] Extra spaces
    - [-] Too bulky: QGraphicsProxyWidget(QGraphicsView(QGraphicsScene(QGraphicsItem)))
    """

    def __init__(self, d: DataValue):
        super().__init__()
        self.setWidget(w := GraphView(d))
        w.setFrameShape(QFrame.Shape.Box)
        # w.setContentsMargins(0, 0, 0, 0)  # ✗
        # experiments:
        # self.setAttribute(Qt.WA_NoSystemBackground)  # ✗
        # self.setAttribute(Qt.WA_TranslucentBackground)  # ✗
        # w.setAttribute(Qt.WA_NoSystemBackground)  # ✗
        # w.setAttribute(Qt.WA_TranslucentBackground)  # ✗


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
