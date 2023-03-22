#!/usr/bin/env python3
"""Testing hints.
RTFM:
- setSizePolicy(QSizePolicy) => QSizePolicy::PolicyFlag (x4)
- size:
  + setMinimumSize()
  + setMaximumSize()
  + setBaseSize()
  + setFixedSize()
- sizeHint()
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


class MainWidget(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)


def main() -> int:
    app = QApplication(sys.argv)
    mw = QMainWindow()
    mw.setCentralWidget(MainWidget(mw))
    mw.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
