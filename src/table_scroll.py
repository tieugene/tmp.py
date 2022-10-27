"""Test QTableWidget.setCellWidget(QScrollArea()) scrolling"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QMainWindow, QTableWidget, QHeaderView, QScrollArea, \
    QScrollBar
# x. const
COL0_WIDTH = 50
ROW_HEIGHt = 15
GFX_WIDTH = 200
GFX_HEIGHT = 20


class MyTable(QTableWidget):
    """
    FIXME: min col1 width == 100
    FIXME: limit MainWindows width with table's one
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setRowCount(5)
        self.setColumnWidth(0, COL0_WIDTH)
        self.horizontalHeader().setStretchLastSection(True)
        # self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.horizontalHeader().setMinimumSectionSize(10)  # not helps
        # self.horizontalScrollBar().setEnabled(False)  # not helps
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for row in range(self.rowCount()):
            sa = QScrollArea()
            widget = QWidget(sa)
            widget.setFixedWidth(GFX_WIDTH)
            widget.setFixedHeight(GFX_HEIGHT)
            sa.setWidget(widget)
            self.setCellWidget(row, 0, QWidget())
            self.setCellWidget(row, 1, sa)
            self.setRowHeight(row, ROW_HEIGHt)
        # self.horizontalHeader().setFirstSectionMovable(False)


class MainWindow(QMainWindow):
    cw: QWidget
    tbl: MyTable
    hsb: QScrollBar

    def __init__(self):
        super().__init__()
        self.__set_widgets()
        self.__set_layout()
        self.setCentralWidget(self.cw)

    def __set_widgets(self):
        self.cw = QWidget(self)
        self.tbl = MyTable(self.cw)
        self.hsb = QScrollBar(Qt.Horizontal)

    def __set_layout(self):
        self.cw.setLayout(QVBoxLayout())
        self.cw.layout().addWidget(self.tbl)
        self.cw.layout().addWidget(self.hsb)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(300, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
