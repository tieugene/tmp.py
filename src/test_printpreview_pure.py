#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import math
import sys
from typing import Tuple

# 2. 3rd
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QIcon, QColor, QPolygonF, QPainterPath, QResizeEvent, QPen, QFont, QPainter, QTransform, QRegion
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, \
    QGraphicsView, QGraphicsScene, QGraphicsPathItem, QDialog, QVBoxLayout, QGraphicsWidget, QGraphicsGridLayout, \
    QGraphicsSimpleTextItem, QGraphicsLayoutItem, QLabel, QWidget, QStyleOptionGraphicsItem, QGraphicsItem, \
    QGraphicsItemGroup

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
        class HeaderItem(QGraphicsSimpleTextItem):
            """Header.
            - [x] TODO: disable scaling
            - [ ] TODO: disable v-resize
            Warn: on resize:
            - not changed: boundingRect(), pos(), scenePos()
            - not call: deviceTransform(), itemTransform(), transform(), boundingRegion()
            - call: paint()
            """
            def __init__(self, parent: QGraphicsItem = None):
                super().__init__(HEADER_TXT, parent)
                self.setFont(FONT_MAIN)
                self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # disable scaling

        class RowItem(QGraphicsItemGroup):
            class LabelItem(QGraphicsSimpleTextItem):
                def __init__(self, d: DataValue, parent: QGraphicsItem = None):
                    super().__init__(d[0], parent)
                    self.setFont(FONT_MAIN)
                    self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

            def __init__(self, d: DataValue, parent: QGraphicsItem = None):
                super().__init__(parent)
                label = self.LabelItem(d)
                self.addToGroup(label)
                graph = Graph(d)
                graph.setX(W_LABEL)
                self.addToGroup(graph)

        def __init__(self, parent: 'ViewWindow' = None):
            super().__init__(parent)
            self.setScene(QGraphicsScene())
            header = self.HeaderItem()
            y = header.boundingRect().height()
            self.scene().addItem(header)
            for r, d in enumerate(DATA[:3]):
                item = self.RowItem(d)
                item.setY(y)
                self.scene().addItem(item)
                y += item.boundingRect().height()

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
