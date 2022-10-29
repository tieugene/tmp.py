#!/usr/bin/env python3
"""QListWidget + Line"""
import sys

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QListWidget, QListWidgetItem, QFrame

ROWS = 5


class LineRow(QListWidgetItem):
    def __init__(self, parent: QListWidget):
        super().__init__(parent)
        line = QFrame()
        line.setGeometry(QRect(0, 0, 100, 3))
        line.setFrameShape(QFrame.HLine)
        parent.setItemWidget(self, line)


class MainWidget(QListWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid grey")
        for i in range(ROWS):
            item_t = QListWidgetItem("test", self)
            # item_t.setFixedHeight(50)  # n/a
            # item_t.setStyleSheet("border: 1px solid red")  # n/a
            item_l = LineRow(self)


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
