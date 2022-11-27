#!/usr/bin/env python3
"""Test of rescaling print (and multipage).
- [ ] FIXME: Label: r-cut
- [ ] FIXME: Plot: shrink v-spaces
- [ ] TODO: Grid: grid lines (a) paint over layout. b) add to each cell item)
Note: now stretch factors depends on (label/graph).boundingRect() ratio
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt, QSizeF, QRectF, QPointF
from PyQt5.QtGui import QIcon, QColor, QResizeEvent, QFont, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsView, \
    QGraphicsScene, QDialog, QVBoxLayout, QGraphicsWidget, QGraphicsGridLayout, QGraphicsLayoutItem, \
    QGraphicsProxyWidget, QFrame, QLabel, QGraphicsItem
# 3. local
from gfx_table_widgets import qsize2str, DataValue, TextItem, GraphItem, GraphView, RectTextItem
from src.gfx_table_widgets import FONT_MAIN, GraphItem, DataValue

# x. const
PPP = 5  # plots per page
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line."
FONT_MAIN = QFont('mono', 8)
W_LABEL = 50  # width of label column
DATA = (  # name, x-offset, color
    ("Signal 1", 0, Qt.GlobalColor.black),
    ("Signal 22", 1, Qt.GlobalColor.red),
    ("Signal 333", 2, Qt.GlobalColor.blue),
    ("Signal 4", 3, Qt.GlobalColor.green),
    ("Signal 5", 4, Qt.GlobalColor.yellow),
    ("Signal 6", 5, Qt.GlobalColor.magenta),
)


def color2style(c: QColor) -> str:
    """Convert QColor into stylesheet-compatible string"""
    return "rgb(%d, %d, %d)" % (c.red(), c.green(), c.blue())


class GridTextItem(QGraphicsLayoutItem):
    """QGraphicsLayoutItem(QGraphicsItem) based.
    Ok:
    - [+] color
    - [+] v-align: top/center
    - [+] v-size: min
    - [-] no cut
    - [-] no border
    """
    __subj: RectTextItem  # must live
    __vcentered: bool

    def __init__(self, txt: str, color: QColor = None, vcentered: bool = False):
        super().__init__()
        self.__subj = RectTextItem(txt, color)
        self.__vcentered = vcentered
        self.setGraphicsItem(self.__subj)
        # experiments:
        self.__subj.bordered = True
        # self.__subj.setFlag(QGraphicsItem.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
        # self.__subj.setFlag(QGraphicsItem.ItemContainsChildrenInShape)

    def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
        if which in {Qt.SizeHint.MinimumSize, Qt.SizeHint.PreferredSize}:
            return self.__subj.boundingRect().size()
        return constraint

    def setGeometry(self, rect: QRectF):  # Warn: Calling once on init
        # print("Text setG:", qsize2str(rect))
        self.__subj.prepareGeometryChange()
        super().setGeometry(rect)
        if self.__vcentered:
            p = QPointF(0, rect.center().y() - self.__subj.boundingRect().height() / 2)
        else:
            p = rect.topLeft()
        self.__subj.setPos(p)


class GridGraphItem(QGraphicsLayoutItem):
    """QGraphicsLayoutItem(QGraphicsItem).
    - [+] Lite
    - [?] Transparent
    - [-] Not fill cell
    """
    __subj: GraphItem

    def __init__(self, d: DataValue):
        super().__init__()
        self.__subj = GraphItem(d)
        self.setGraphicsItem(self.__subj)
        self.__subj.bordered = True
        # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # ✗

    def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
        """Calling 3 times at start; has no effect.
        Constraint default = (-1, -1)
        """
        # if which in {Qt.MinimumSize, Qt.PreferredSize}:
        #   return QSizeF(0, 0)  # h must be same as on init
        return constraint

    def setGeometry(self, rect: QRectF):
        """Calling once on init"""
        # print("Graph setG:", qsize2str(rect))
        self.__subj.prepareGeometryChange()
        super().setGeometry(rect)
        self.__subj.setPos(rect.topLeft())
        # TODO: resize item to rect

    # def boundingRect(self) -> QRectF:
    #    return QRectF(QPointF(0, 0), self.geometry().size())


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


class ViewWindow(QDialog):
    class Plot(QGraphicsView):
        def __init__(self, parent: 'ViewWindow' = None):
            super().__init__(parent)
            self.setScene(QGraphicsScene())
            self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)  # ✗
            lt = QGraphicsGridLayout()
            # lt.addItem(TextGfxWidget(HEADER_TXT), 0, 0, 1, 2)  # ✗ (span)
            for row, d in enumerate(DATA[:3]):
                lt.addItem(GridTextItem(d[0], d[2], False), row, 0)  # A: GridTextItem, B: TextGfxWidget
                lt.addItem(GridGraphItem(d), row, 1)
                # lt.setRowFixedHeight(row, 100)  # works strange
                # lt.setRowSpacing(row, 0)  # ✗
                lt.setRowStretchFactor(row, row)  # ✗
            # Layout tuning
            lt.setSpacing(0)
            lt.setContentsMargins(0, 0, 0, 0)
            # lt.setRowFixedHeight(0, 50)  # ✗
            # go
            gw = QGraphicsWidget()
            gw.setLayout(lt)
            self.scene().addItem(gw)

        def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
            self.fitInView(self.sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)  # expand to max

    def __init__(self, parent: 'MainWindows'):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.Plot(self))


class MainWidget(QTableWidget):

    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setRowCount(len(DATA))
        self.setColumnCount(2)
        for r, d in enumerate(DATA):
            self.setItem(r, 0, (QTableWidgetItem(d[0])))
            self.setCellWidget(r, 1, GraphView(d))


class MainWindow(QMainWindow):
    view: ViewWindow

    def __init__(self):
        super().__init__()
        self.setCentralWidget(MainWidget(self))
        self.view = ViewWindow(self)
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(QAction(QIcon.fromTheme("view-fullscreen"), "&View", self, shortcut="Ctrl+V",
                                    triggered=self.__view))
        menu_file.addAction(QAction(QIcon.fromTheme("document-print-preview"), "&Print", self, shortcut="Ctrl+P",
                                    triggered=self.__print))
        menu_file.addAction(QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                    triggered=self.close))
        self.menuBar().setVisible(True)

    def __view(self):
        self.view.show()

    def __print(self):
        ...


def main() -> int:
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    # mw.resize(600, 600)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())


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
