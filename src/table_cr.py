"""Test table with multiline cell"""
# 1. std
import sys

from PyQt5.QtGui import QIcon
# 2. 3rd
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidget, QTableWidgetItem, QListWidget, \
    QVBoxLayout, QListWidgetItem


class MyTable(QTableWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setRowCount(3)
        # data
        self.setItem(0, 0, QTableWidgetItem("123\nabc"))
        self.setItem(1, 0, QTableWidgetItem("456\ndef"))
        self.setItem(1, 0, QTableWidgetItem("789\nghi"))
        # ui
        self.horizontalHeader().setStretchLastSection(True)
        # selection
        self.setSelectionMode(self.SingleSelection)
        self.setSelectionBehavior(self.SelectRows)
        # DnD
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)  # False: Over/B2in; True/default: Over only
        self.setDropIndicatorShown(True)
        self.setDragDropMode(self.DragDrop)  # was self.InternalMove


class MyList(QListWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        # data
        self.addItem(QListWidgetItem(QIcon.fromTheme("edit-undo"), "123\nABC", self))
        self.addItem(QListWidgetItem("456\nDEF"))
        self.addItem(QListWidgetItem("789\nGHI"))
        # selection
        self.setSelectionMode(self.SingleSelection)
        # self.setSelectionBehavior(self.SelectRows)
        # DnD
        self.setDragEnabled(True)
        # self.setAcceptDrops(False)  # default False
        # self.viewport().setAcceptDrops(True)
        # self.setDragDropOverwriteMode(False)
        # self.setDropIndicatorShown(True)
        # self.setDragDropMode(self.DragDrop)  # was self.InternalMove


class MainWindow(QMainWindow):
    cw: QWidget
    tbl: MyTable
    lst: MyList

    def __init__(self):
        super().__init__()
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        self.tbl = MyTable(self.cw)
        self.lst = MyList(self.cw)
        self.cw.setLayout(QVBoxLayout())
        self.cw.layout().addWidget(self.tbl)
        self.cw.layout().addWidget(self.lst)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(300, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
