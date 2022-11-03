#!/usr/bin/env python3
"""QListWidget + Line"""
import sys

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame, QTableWidget, QHeaderView

ROWS = 5
LINE_CELL_SIZE = 1  # width ow VLine column / height of HLine row


class HLine(QFrame):
    __row: int

    def __init__(self, row: int, parent=None):
        """Parents: QWidget<MainWidget"""
        super().__init__(parent)
        self.__row = row
        self.setGeometry(QRect(0, 0, 0, 0))  # size is not the matter
        self.setFrameShape(QFrame.HLine)
        self.setCursor(Qt.SplitVCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """accepted() == True, y() = Δy"""
        (tbl := self.parent().parent()).setRowHeight(self.__row - 1, tbl.rowHeight(self.__row - 1) + event.y())


class VLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(QRect(0, 0, 0, 0))  # size is not the matter
        self.setFrameShape(QFrame.VLine)
        self.setCursor(Qt.SplitHCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """accepted() == True, x() = Δx"""
        (tbl := self.parent().parent()).setColumnWidth(0, tbl.columnWidth(0) + event.x())


class MainWidget(QTableWidget):
    """TODO: update HLine.row's on row remove/insert"""

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        # self.setStyleSheet("border: 1px solid grey")
        self.setColumnCount(3)
        self.setRowCount(ROWS * 2)
        self.horizontalHeader().setMinimumSectionSize(1)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        self.setColumnWidth(1, LINE_CELL_SIZE)
        self.verticalHeader().setMinimumSectionSize(1)
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # not helps
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # not helps
        self.setShowGrid(False)
        for i in range(ROWS):
            self.setCellWidget(i * 2, 0, QLabel(f"Row {i}"))
            self.setCellWidget(i * 2, 1, VLine(self))
            self.setCellWidget(i * 2 + 1, 0, HLine(i * 2 + 1, self))
            self.setCellWidget(i * 2 + 1, 1, HLine(i * 2 + 1, self))
            self.setCellWidget(i * 2 + 1, 2, HLine(i * 2 + 1, self))
            self.setRowHeight(i * 2 + 1, LINE_CELL_SIZE)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(MainWidget(self))


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
