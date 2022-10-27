#!/bin/env python3
"""iOsc.py layout demo."""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsScene, QScrollArea, \
    QWidget, QScrollBar, QSplitter, QAction, QTabWidget


class XScaleLabel(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__('ms', parent)
        self.setStyleSheet('{color: grey}')


class XScaleItself(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__('xscal', parent)
        self.setStyleSheet('{background: yellow;}')


class XScaleRow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setStyleSheet('{border: 1px solid black;}')
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(XScaleLabel(self))
        self.layout().addWidget(XScaleItself(self))


class MainRow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel("middle", self))


class StatusRow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel("status", self))


class ScrollRow(QScrollBar):
    def __init__(self, parent: QWidget):
        super().__init__(Qt.Horizontal, parent)


class MainTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(XScaleRow(self))
        self.layout().addWidget(MainRow(self))
        self.layout().addWidget(StatusRow(self))
        self.layout().addWidget(ScrollRow(self))
        self.layout().setStretch(0, 0)
        self.layout().setStretch(1, 1)
        self.layout().setStretch(2, 0)
        self.layout().setStretch(3, 0)


class MainTabWidget(QTabWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.addTab(MainTab(self), "Main")


class MainWindow(QMainWindow):
    # widgets
    xscale_label: QLabel
    xscale_widget: QGraphicsScene
    xscale_h_scroll_area: QScrollArea
    top_left_widgets: list[QWidget]
    top_v_splitter: QSplitter
    top_rite_scroll_area: QScrollArea
    top_rite_widgets: list[QWidget]
    top_v_scroll_area: QScrollArea
    mid_h_splitter: QSplitter
    bot_v_scroll_area: QScrollArea
    bot_left_widgets: list[QWidget]
    bot_v_spliier: QSplitter
    bot_rite_scroll_area: QScrollArea
    bot_rite_widgets: list[QWidget]
    bot_status_bar: QGraphicsScene
    bot_scroll_bar: QScrollBar
    # layouts
    main_v_layout: QVBoxLayout
    xscale_h_layout: QHBoxLayout
    mid_v_layout: QHBoxLayout
    top_h_layout: QHBoxLayout
    top_left_v_layout: QVBoxLayout
    top_rite_v_layout: QVBoxLayout
    bot_h_layout: QHBoxLayout
    bot_left_v_layout: QVBoxLayout
    bot_rite_v_layout: QVBoxLayout

    def __init__(self):
        super().__init__()
        self.tabs = MainTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.setWindowTitle("iOsc.py")
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(QAction(
            QIcon.fromTheme("application-exit"),
            "E&xit",
            self,
            shortcut="Ctrl+Q",
            triggered=self.close)
        )


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(800, 600)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
