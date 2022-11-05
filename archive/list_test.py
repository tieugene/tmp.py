#!/usr/bin/env python3
"""QListWidget + Line"""
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QAction, QMenuBar


class MainWidget(QListWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid grey")
        for i in range(5):
            QListWidgetItem(f"test{i}", self)


class MainWindow(QMainWindow):
    """Main window"""
    cw: MainWidget

    def __init__(self):
        super().__init__()
        self.cw = MainWidget(self)
        self.setCentralWidget(self.cw)
        self.menuBar().addMenu("&File").addAction("&Test", self, shortcut="Ctrl+T", triggered=self.__do_test))

    def __do_test(self):
        print("Before:", self.cw.count())
        item = self.cw.takeItem(3)
        del item
        print("After:", self.cw.count())


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
