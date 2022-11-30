#!/usr/bin/env python3
"""Test of rescaling print (and multipage)."""
# 1. std
import sys
from typing import List
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QAction, QTableWidgetItem, QGraphicsWidget,\
    QGraphicsLinearLayout, QActionGroup, QShortcut
# 3. local
from gfx_ppreview_const import DATA, DataValue, W_PAGE, H_ROW_BASE
from gfx_ppreview_widgets import GraphView, RowItem, LayoutItem, GraphViewBase, HeaderItem, BottomItem


class TableItem(QGraphicsWidget):
    def __init__(self, dlist: List[DataValue], plot: 'Plot'):
        super().__init__()
        lt = QGraphicsLinearLayout(Qt.Vertical, self)
        lt.setSpacing(0)
        lt.addItem(LayoutItem(HeaderItem(plot)))
        for row, d in enumerate(dlist):
            lt.addItem(LayoutItem(RowItem(d, plot)))
        lt.addItem(LayoutItem(BottomItem(plot)))
        self.setLayout(lt)

    def update_sizes(self):
        for i in range(self.layout().count()):
            self.layout().itemAt(i).graphicsItem().update_size()


class Plot(GraphViewBase):
    __father: 'MainWindow'
    __portrait: bool
    __table: TableItem
    # shortcuts
    __sc_close: QShortcut
    __sc_size0: QShortcut
    __sc_o_L: QShortcut
    __sc_o_P: QShortcut

    def __init__(self, father: 'MainWindow'):
        super().__init__()
        self.__father = father
        self.__portrait = False
        self.__table = TableItem(DATA[:6], self)
        self.scene().addItem(self.__table)
        # shortcuts
        self.__sc_close = QShortcut("Ctrl+V", self)
        self.__sc_size0 = QShortcut("Ctrl+0", self)
        self.__sc_o_L = QShortcut("Ctrl+L", self)
        self.__sc_o_P = QShortcut("Ctrl+P", self)
        # ...and their connections
        self.__sc_close.activated.connect(self.close)
        self.__sc_size0.activated.connect(self.slot_reset_size)
        self.__sc_o_L.activated.connect(self.__slot_set_o_l)
        self.__sc_o_P.activated.connect(self.__slot_set_o_p)

    @property
    def w_full(self) -> int:
        """Current full table width"""
        return W_PAGE[int(self.__portrait)]

    @property
    def h_row_base(self) -> int:
        """Current base (short) row height.
        :note: in theory must be (W_PAGE - header - footer) / num
        :todo: cache it
        """
        return round(H_ROW_BASE * 1.5) if self.__portrait else H_ROW_BASE

    @property
    def portrait(self) -> bool:
        return self.__portrait

    @portrait.setter
    def portrait(self, v: bool):
        # FIXME: shrink width
        if self.__portrait ^ v:
            self.__portrait = v
            self.__table.update_sizes()
            # self.setSceneRect(self.scene().itemsBoundingRect())  # not works
            # self.slot_reset_size()

    def __slot_set_o_l(self):
        self.portrait = False

    def __slot_set_o_p(self):
        self.portrait = True

    def slot_reset_size(self):
        """[Re]set view to original size."""
        self.resize(self.scene().itemsBoundingRect().size().toSize())

    def closeEvent(self, _: QCloseEvent):
        """Masq closing with switch off"""
        self.__father.act_view.setChecked(False)


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
    view: Plot
    act_view: QAction
    act_o_l: QAction
    act_o_p: QAction
    act_o: QActionGroup

    def __init__(self):
        super().__init__()
        self.setCentralWidget(MainWidget(self))
        self.view = Plot(self)
        self.__mk_actions()

    def __mk_actions(self):
        # grouping
        self.act_o_l = QAction(QIcon.fromTheme("object-flip-horizontal"), "Landscape", self, shortcut="Ctrl+L",
                               checkable=True)
        self.act_o_p = QAction(QIcon.fromTheme("object-flip-vertical"), "Portrait", self, shortcut="Ctrl+P",
                               checkable=True)
        self.act_o = QActionGroup(self)
        self.act_o.addAction(self.act_o_l).setChecked(True)
        self.act_o.addAction(self.act_o_p)
        self.act_o.triggered.connect(self.__do_o)
        self.act_view = QAction(QIcon.fromTheme("view-fullscreen"), "&View", self, shortcut="Ctrl+V", checkable=True,
                                toggled=self.__do_view)
        # menu
        self.menuBar().setVisible(True)
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_view)
        menu_file.addAction(QAction(QIcon.fromTheme("document-print-preview"), "&Print", self, shortcut="Ctrl+P",
                                    triggered=self.__do_print))
        menu_file.addAction(QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                    triggered=self.close))
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(QAction(QIcon.fromTheme("zoom-original"), "Original size", self, shortcut="Ctrl+0",
                                    triggered=self.view.slot_reset_size))
        menu_view.addAction(self.act_o_l)
        menu_view.addAction(self.act_o_p)

    def __do_o(self, a: QAction):
        """Switch page orientation"""
        self.view.portrait = (a == self.act_o_p)

    def __do_view(self, v: bool):
        """Switch View on/off"""
        self.view.setVisible(v)

    def __do_print(self):
        ...


def main() -> int:
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    # mw.resize(600, 600)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
