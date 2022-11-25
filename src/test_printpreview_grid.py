#!/usr/bin/env python3
"""Test of rescaling print (and multipage).
- [x] grid lines
- [ ] cut labels
- [ ] resize plots
"""
# 1. std
import math
import sys
from typing import Tuple
# 2. 3rd
from PyQt5.QtCore import Qt, QPointF, QSizeF, QRectF, QRect, QMargins
from PyQt5.QtGui import QIcon, QColor, QPolygonF, QPainterPath, QResizeEvent, QPen, QFont, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, \
    QGraphicsView, QGraphicsScene, QGraphicsPathItem, QDialog, QVBoxLayout, QGraphicsWidget, QGraphicsGridLayout, \
    QGraphicsSimpleTextItem, QGraphicsLayoutItem, QLabel, QGraphicsItem, QGraphicsProxyWidget, QFrame, QWidget

# x. const
DataValue = Tuple[str, int, QColor]
PPP = 5  # plots per page
POINTS = 12
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line."
FONT_MAIN = QFont('mono', 8)
W_LABEL = 50  # width of label column
DATA = (  # name, x-offset, color
    ("Signal 1", 0, Qt.black),
    ("Signal 2", 1, Qt.yellow),
    ("Signal 3", 2, Qt.blue),
    ("Signal 4", 3, Qt.green),
    ("Signal 5", 4, Qt.red),
    ("Signal 6", 5, Qt.magenta),
)


def mk_sin(o: int = 0) -> list[float]:
    """
    Make sinusoide graph coordinates. Y=0..1
    :param o: Offset, points
    :return: list of y (0..1)
    """
    return [(1 + math.sin((i + o) * 2 * math.pi / POINTS)) / 2 for i in range(POINTS + 1)]


def color2style(c: QColor) -> str:
    """Convert QColor into stylesheet-compatible string"""
    return "rgb(%d, %d, %d)" % (c.red(), c.green(), c.blue())


class Graph(QGraphicsPathItem):
    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        pg = QPolygonF([QPointF(x * 50, y * 100) for x, y in enumerate(mk_sin(d[1]))])
        pp = QPainterPath()
        pp.addPolygon(pg)
        self.setPath(pp)
        pen = QPen(d[2])
        pen.setCosmetic(True)  # !!! don't resize pen width
        self.setPen(pen)


class ViewWindow(QDialog):
    class Plot(QGraphicsView):
        class HLineGridWidget(QGraphicsProxyWidget):
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

        class VLineGridWidget(QGraphicsProxyWidget):
            def __init__(self):
                super().__init__()
                self.setWidget(w := QFrame())
                w.setFrameShape(QFrame.VLine)
                w.setLineWidth(0)

        class TextGridWidget(QGraphicsProxyWidget):
            """QWidget based"""
            def __init__(self, txt: str, color: QColor = None):
                super().__init__()
                self.setWidget(w := QLabel(txt))
                w.setFont(FONT_MAIN)
                if color:
                    # plan A
                    p = QPalette()
                    p.setColor(QPalette.WindowText, color)
                    w.setPalette(p)
                    # plan B
                    # w.setStyleSheet("color: %s" % color2style(color))
                self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

        class TextGridItem(QGraphicsLayoutItem):
            """QGraphicsItem based"""
            __subj: QGraphicsSimpleTextItem

            def __init__(self, txt: str, color: QColor = None):
                super().__init__()
                self.__subj = QGraphicsSimpleTextItem(txt)  # must be alive forewer
                self.__subj.setFont(FONT_MAIN)
                if color:
                    pen = self.__subj.pen()
                    pen.setColor(color)  # FIXME: not helps (always black)
                    self.__subj.setPen(pen)
                self.setGraphicsItem(self.__subj)
                self.graphicsItem().setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # Not helps
                # replace/help sizeHint()  (not helps)
                # size = self.__subj.boundingRect().size()
                # self.setMinimumWidth(size.width())
                # self.setMinimumHeight(size.height())

            def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
                if which in {Qt.MinimumSize, Qt.PreferredSize}:
                    return self.__subj.boundingRect().size()
                return constraint

            def setGeometry(self, rect: QRectF):
                self.__subj.prepareGeometryChange()
                super().setGeometry(rect)
                self.__subj.setPos(rect.topLeft())
                # TODO: cut

        class PlotGridItem(QGraphicsLayoutItem):
            __subj: Graph

            def __init__(self, d: DataValue):
                super().__init__()
                self.__subj = Graph(d)
                self.setGraphicsItem(self.__subj)

            def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
                return constraint

            def setGeometry(self, rect: QRectF):
                self.__subj.prepareGeometryChange()
                super().setGeometry(rect)
                self.__subj.setPos(rect.topLeft())
                # FIXME: set size

        def __init__(self, parent: 'ViewWindow' = None):
            super().__init__(parent)
            self.setScene(QGraphicsScene())
            lt = QGraphicsGridLayout()
            lt.setSpacing(0)
            lt.setContentsMargins(0, 0, 0, 0)
            lt.addItem(self.HLineGridWidget(), 0, 0, 1, 5)
            for i, d in enumerate(DATA[:3]):
                row = i * 2 + 1
                lt.addItem(self.TextGridWidget(d[0], d[2]), row, 1)  # plan A (good colored, good cut)
                # lt.addItem(self.TextGridItem(d[0], d[2]), row, 1)  # plan B
                lt.addItem(self.PlotGridItem(d), row, 3)
                for c in (0, 2, 4):
                    lt.addItem(self.VLineGridWidget(), row, c)
                lt.addItem(self.HLineGridWidget(), row + 1, 0, 1, 5)
            gw = QGraphicsWidget()
            gw.setLayout(lt)
            self.scene().addItem(gw)

        def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
            self.fitInView(self.sceneRect(), Qt.IgnoreAspectRatio)  # expand to max

    def __init__(self, parent: 'MainWindows'):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.Plot(self))


class MainWidget(QTableWidget):
    class Plot(QGraphicsView):
        def __init__(self, d: tuple[str, int, QColor]):
            super().__init__()
            self.setScene(QGraphicsScene())
            self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
            self.scene().addItem(Graph(d))

        def resizeEvent(self, event: QResizeEvent):  # !!! (resize view to content)
            # super().resizeEvent(event)
            self.fitInView(self.sceneRect(), Qt.IgnoreAspectRatio)  # expand to max
            # Note: KeepAspectRatioByExpanding is extremally CPU-greedy

    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setRowCount(len(DATA))
        self.setColumnCount(2)
        for r, d in enumerate(DATA):
            self.setItem(r, 0, (QTableWidgetItem(d[0])))
            self.setCellWidget(r, 1, self.Plot(d))


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
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
