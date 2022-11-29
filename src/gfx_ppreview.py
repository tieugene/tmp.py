#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import sys
from typing import List

# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QDialog, QVBoxLayout, \
    QGraphicsWidget, QGraphicsLinearLayout, QToolBar, QActionGroup, QSizePolicy, QLayout
# 3. local
from gfx_ppreview_const import DATA, DataValue, W_PAGE, H_ROW_BASE
from gfx_ppreview_widgets import GraphView, RowItem, LayoutItem, GraphViewBase, HeaderItem, qsize2str


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

    # def sizeHint(self) -> QSize:  # not helps
    #    return self.scene().itemsBoundingRect().size().toSize()

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

    def reset_size(self):
        """[Re]set view to original size.
        .viewport().resize(): not works
        .setSceneRect(): not works
        .setFixedSize(): too strict
        """
        size = self.scene().itemsBoundingRect().size().toSize()
        # print(qsize2str(size))
        self.resize(size)
        self.parent().adjustSize()  # "The maximum size of a window is 2/3 of the screen's width and height."


class ViewWindow(QDialog):
    __plot: Plot
    act_size0: QAction  # [re]set size to original
    act_o: QActionGroup
    act_o_L: QAction  # landscape
    act_o_P: QAction  # portrait
    tb: QToolBar

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.__plot = Plot(self)
        self.__mk_actions()
        self.__mk_toolbar()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tb)
        self.layout().addWidget(self.__plot)
        # experiments
        self.layout().setSpacing(0)
        # self.layout().setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        # self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

    def __mk_actions(self):
        self.act_size0 = QAction(QIcon.fromTheme("zoom-original"), "Original size", self, shortcut="Ctrl+0",
                                 triggered=self.__plot.reset_size)
        self.act_o_L = QAction(QIcon.fromTheme("object-flip-horizontal"), "Landscape", self, shortcut="Ctrl+L",
                               checkable=True)
        self.act_o_P = QAction(QIcon.fromTheme("object-flip-vertical"), "Portrait", self, shortcut="Ctrl+P",
                               checkable=True)
        self.act_o = QActionGroup(self)
        self.act_o.addAction(self.act_o_L).setChecked(True)
        self.act_o.addAction(self.act_o_P)
        self.act_o.triggered.connect(self.__do_o)

    def __mk_toolbar(self):
        self.tb = QToolBar(self)
        self.tb.addAction(self.act_size0)
        self.tb.addAction(self.act_o_L)
        self.tb.addAction(self.act_o_P)

    def __do_o(self, a: QAction):
        """Switch page orientation"""
        ...


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
