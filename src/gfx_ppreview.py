#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import sys
from typing import List

# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QDialog, QVBoxLayout,\
    QGraphicsWidget, QGraphicsLinearLayout
# 3. local
from gfx_ppreview_const import DATA, DataValue, W_PAGE, H_ROW_BASE
from gfx_ppreview_widgets import GraphView, RowItem, LayoutItem, GraphViewBase, HeaderItem


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue], plot: 'Plot'):
        super().__init__()
        lt = QGraphicsLinearLayout(Qt.Vertical, self)
        lt.setSpacing(0)
        lt.addItem(LayoutItem(HeaderItem(plot)))
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RowItem(d, plot)))
        self.setLayout(lt)

    def update_sizes(self):
        for i in range(self.layout().count()):
            self.layout().itemAt(i).graphicsItem().update_size()


class Plot(GraphViewBase):
    portrait: bool

    def __init__(self, parent: 'ViewWindow'):
        super().__init__(parent)
        self.portrait = False
        self.scene().addItem(TableItem(DATA[:6], self))

    @property
    def w_full(self) -> int:
        """Current full table width"""
        return W_PAGE[int(self.portrait)]

    @property
    def h_row_base(self) -> int:
        """Current base (short) row height.
        :note: in theory must be (W_PAGE - header - footer) / num
        :todo: cache it
        """
        return round(H_ROW_BASE * 1.5) if self.portrait else H_ROW_BASE


class ViewWindow(QDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(Plot(self))


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
