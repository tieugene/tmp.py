#!/usr/bin/env python3
"""Test QScrollBar behaviour on page/range change.
Result:
- on range changed value _not_ changed
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QToolBar, QLabel, QScrollBar, QVBoxLayout

SB_BASE = 100


class MainWidget(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        # vars
        self.page_x = 1
        self.range_x = 1
        # actions
        act_range_inc = QAction("<[]>", self, triggered=self.__do_range_inc)
        act_range_dec = QAction(">[]<", self, triggered=self.__do_range_dec)
        act_page_inc = QAction("<->", self, triggered=self.__do_page_inc)
        act_page_dec = QAction(">-<", self, triggered=self.__do_page_dec)
        # menu
        # parent.menuBar().addMenu("&File").addAction("&Test", self, shortcut="Ctrl+T", triggered=self.__do_test)
        # toolbar
        tb = QToolBar(self)
        tb.addAction(act_range_inc)
        tb.addAction(act_range_dec)
        tb.addAction(act_page_inc)
        tb.addAction(act_page_dec)
        # widgets
        self.label = QLabel(self)
        self.sb = QScrollBar(Qt.Horizontal, self)
        # layout
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(tb)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.sb)
        # init
        self.sb.setValue(0)
        self.sb.setRange(0, 100)
        self.sb.setPageStep(100)
        # go
        self.__update_label()
        self.sb.valueChanged.connect(self.__update_label)

    def __chg_range(self, dx: int):
        if self.range_x + dx > 0:
            self.range_x += dx
            self.sb.setRange(0, self.range_x * SB_BASE)
            self.__update_label()

    def __do_range_inc(self):
        self.__chg_range(1)

    def __do_range_dec(self):
        self.__chg_range(-1)

    def __chg_page(self, dx: int):
        if self.page_x + dx > 0:
            self.page_x += dx
            self.sb.setPageStep(self.page_x * SB_BASE)
            self.__update_label()

    def __do_page_inc(self):
        self.__chg_page(1)

    def __do_page_dec(self):
        self.__chg_page(-1)

    def __update_label(self):
        self.label.setText("v = %d / %d + %d" % (self.sb.value(), self.sb.maximum(), self.sb.pageStep()))


def main() -> int:
    app = QApplication(sys.argv)
    mw = QMainWindow()
    mw.setCentralWidget(MainWidget(mw))
    mw.show()
    mw.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
