#!/usr/bin/env python3
"""Test of rescaling print (and multipage).
Resume: setStretch, setHeight not work
- [ ] FIXME: Label: r-cut
- [ ] FIXME: Plot: shrink v-spaces
- [ ] TODO: Grid: grid lines (a) paint over layout. b) add to each cell item)
Note: now stretch factors depends on (label/graph).boundingRect() ratio
"""
# 1. std
import sys
from typing import List

# 2. 3rd
from PyQt5.QtCore import Qt, QSizeF, QRectF
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsView, \
    QGraphicsScene, QDialog, QVBoxLayout, QGraphicsWidget, QGraphicsGridLayout, QGraphicsLayoutItem, QGraphicsItem
# 3. local
from gfx_table_widgets import W_LABEL, DataValue, HEADER_TXT, DATA, TextItem, RectTextItem, GraphItem, GraphView


class TableItem(QGraphicsWidget):
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
            # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
            # self.__subj.setFlag(QGraphicsItem.ItemContainsChildrenInShape)
            # self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # ✗

        def sizeHint(self, which: Qt.SizeHint, constraint: QSizeF = ...) -> QSizeF:
            if which in {Qt.SizeHint.MinimumSize, Qt.SizeHint.PreferredSize}:
                return self.__subj.boundingRect().size()
            return constraint

        def setGeometry(self, rect: QRectF):  # Warn: Calling once on init
            self.__subj.prepareGeometryChange()
            super().setGeometry(rect)
            self.__subj.setPos(rect.topLeft())

    def __init__(self, dlist: List[DataValue]):
        super().__init__()
        lt = QGraphicsGridLayout()
        # lt.addItem(TextGfxWidget(HEADER_TXT), 0, 0, 1, 2)  # ✗ (span)
        for row, d in enumerate(dlist):
            lt.addItem(self.LayoutItem(RectTextItem(W_LABEL, d[0], d[2])), row, 0)  # A: GridTextItem, B: TextGfxWidget
            lt.addItem(self.LayoutItem(GraphItem(d)), row, 1)
            # lt.setRowFixedHeight(row, 100)  # works strange
            # lt.setRowSpacing(row, 0)  # ✗
            lt.setRowStretchFactor(row, row)  # ✗
        # Layout tuning
        lt.setSpacing(0)
        lt.setContentsMargins(0, 0, 0, 0)
        # lt.setRowFixedHeight(0, 50)  # ✗
        self.setLayout(lt)


class ViewWindow(QDialog):
    class Plot(QGraphicsView):
        def __init__(self, parent: 'ViewWindow' = None):
            super().__init__(parent)
            self.setScene(QGraphicsScene())
            self.scene().addItem(header := TextItem(HEADER_TXT))
            self.scene().addItem(table := TableItem(DATA[:3]))
            table.setPos(0, header.boundingRect().height())
            # self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)  # ✗

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
