#!/usr/bin/env python3
"""Test of rescaling print (and multipage).
- [x] grid lines
- [ ] cut labels
- [ ] resize plots
"""
# 1. std
import sys
from typing import Optional
# 2. 3rd
from PyQt5.QtCore import Qt, QSizeF, QRectF
from PyQt5.QtGui import QIcon, QColor, QResizeEvent, QFont, QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsView,\
    QGraphicsScene, QDialog, QVBoxLayout, QGraphicsWidget, QGraphicsGridLayout, QGraphicsLayoutItem, QGraphicsItem,\
    QGraphicsProxyWidget, QFrame, QWidget, QStyleOptionGraphicsItem

from src.gfx_table_widgets import DataValue, TextItem, GraphItem, GraphWidget, TextWidget

# x. const
PPP = 5  # plots per page
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line."
FONT_MAIN = QFont('mono', 8)
W_LABEL = 50  # width of label column
DATA = (  # name, x-offset, color
    ("Signal 1", 0, Qt.black),
    ("Signal 2", 1, Qt.red),
    ("Signal 3", 2, Qt.blue),
    ("Signal 4", 3, Qt.green),
    ("Signal 5", 4, Qt.yellow),
    ("Signal 6", 5, Qt.magenta),
)


def color2style(c: QColor) -> str:
    """Convert QColor into stylesheet-compatible string"""
    return "rgb(%d, %d, %d)" % (c.red(), c.green(), c.blue())


class TextGridItem(QGraphicsLayoutItem):
    """QGraphicsItem based"""
    __subj: TextItem

    def __init__(self, txt: str, color: QColor = None):
        super().__init__()
        self.__subj = TextItem(txt, color)  # must be alive forewer
        self.setGraphicsItem(self.__subj)
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
    __subj: GraphItem

    def __init__(self, d: DataValue):
        super().__init__()
        self.__subj = GraphItem(d)
        self.setGraphicsItem(self.__subj)

    def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
        match which:
            case Qt.MinimumSize | Qt.PreferredSize:
                return QSizeF(50, 20)
            case Qt.MaximumSize:
                return QSizeF(1000, 1000)
        return constraint

    def setGeometry(self, rect: QRectF):
        self.__subj.prepareGeometryChange()
        super().setGeometry(rect)
        self.__subj.setPos(rect.topLeft())
        # FIXME: set size


class TextGridWidget(QGraphicsProxyWidget):  # <= QGraphicsWidget
    """QWidget based.
    TODO: self.paintWindowFrame()
    """
    def __init__(self, txt: str, color: QColor = None):
        super().__init__()
        w = TextWidget(txt, color)
        self.setWidget(w)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

    def boundingRect(self):
        """Seems not works"""
        return QGraphicsProxyWidget.boundingRect(self).adjusted(0, 0, 10, 10)

    def paintWindowFrame(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...):
        """Not works.
        RTFM examples/../embeddeddialogs
        """
        print("Go!")
        painter.setPen(Qt.black)
        painter.setBrush(Qt.red)
        painter.drawRect(self.windowFrameRect())
        super().paintWindowFrame(painter, option, widget)


class PlotGridWidget(QGraphicsWidget):  # QGraphicsObject + QGraphicsLayoutItem
    __subj: GraphItem

    def __init__(self, d: DataValue, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.__subj = GraphItem(d, self)
        self.setGraphicsItem(self.__subj)
        # w = QWidget()
        # w.setLayout(QVBoxLayout())
        # w.layout().addWidget(GraphItem(d))
        # self.setWidget(w)  # GraphItem(d)


class PlotGridProxyWidget(QGraphicsProxyWidget):  # <= QGraphicsWidget
    """QWidget based"""
    def __init__(self, d: DataValue):
        super().__init__()
        w = GraphWidget(d)
        w.setFrameShape(QFrame.Box)
        self.setWidget(w)


class ViewWindow(QDialog):
    class Plot(QGraphicsView):

        def __init__(self, parent: 'ViewWindow' = None):
            super().__init__(parent)
            self.setScene(QGraphicsScene())
            lt = QGraphicsGridLayout()
            lt.setSpacing(0)
            lt.setContentsMargins(0, 0, 0, 0)
            # lt.addItem(self.HLineGridWidget(), 0, 0, 1, 5)
            for i, d in enumerate(DATA[:3]):
                row = i * 2 + 1
                # plan A: self.TextGridWidget (good colored, good cut)
                # plan B: self.TextGridItem
                lt.addItem(TextGridItem(d[0], d[2]), row, 0)
                lt.addItem(PlotGridProxyWidget(d), row, 1)
                # for c in (0, 2, 4):
                #    lt.addItem(self.VLineGridWidget(), row, c)
                # lt.addItem(self.HLineGridWidget(), row + 1, 0, 1, 5)
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

    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        self.horizontalHeader().setStretchLastSection(True)
        self.setRowCount(len(DATA))
        self.setColumnCount(2)
        for r, d in enumerate(DATA):
            self.setItem(r, 0, (QTableWidgetItem(d[0])))
            self.setCellWidget(r, 1, GraphWidget(d))


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
