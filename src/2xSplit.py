#!/usr/bin/env python3
"""2x splitters"""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QLabel, QScrollArea, QGridLayout, \
    QHBoxLayout, QSizePolicy

ROWS = 3
COLS = 2


class Cell(QLabel):
    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.setStyleSheet("border: 1px solid grey")


class Row(QSplitter):
    def __init__(self, parent: QMainWindow):
        super().__init__(Qt.Horizontal, parent)
        # self.setFixedHeight(50)

        self.addWidget(Cell("Left", self))
        self.addWidget(Cell("Right", self))


class MainWidget(QScrollArea):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("border: 1px solid green")
        # self.setWidgetResizable(True)  # dont do this
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("border: 1px solid red")
        print(splitter.sizePolicy())
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # splitter.setHandleWidth(1)  # no effect
        for i in range(10):
            row = Cell(f"Cell{i}")
            splitter.addWidget(row)
            splitter.setStretchFactor(i, 0)
        self.setWidget(splitter)


class MainWindow(QMainWindow):
    """Main window"""
    cw: MainWidget

    def __init__(self):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.cw = MainWidget(self)
        self.layout().addWidget(self.cw)
        self.setCentralWidget(self.cw)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
