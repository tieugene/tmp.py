#!/usr/bin/env python3
"""Sample QTableWidget:
Лента: ribbon, band, lane, strip, set, bar
"""
import random
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt, QObject, QMargins
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QWidget, QMainWindow, QVBoxLayout, QApplication, QSplitter, \
    QPushButton, QHBoxLayout
from QCustomPlot2 import QCustomPlot, QCPGraph
#  x. const
COLORS = (Qt.black, Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.gray)
BARS = 3
SIN_SAMPLES = 72  # 5°


class TopBar(QWidget):
    def __init__(self, parent: 'MainWidget'):
        super().__init__(parent)


class SignalLabel(QListWidgetItem):
    def __init__(self, parent: 'SignalLabelList' = None):
        super().__init__(parent)


class SignalPlot(QCustomPlot):
    def __init__(self, parent: 'SignalPlotWidget'):
        super().__init__(parent)


class SignalSet(QObject):
    __bar: 'SignalBar'
    __name: str
    __num: int
    __off: int
    __color: Qt.GlobalColor
    __label: SignalLabel
    __graph: SignalPlot

    def __init__(self, name: str, num: int, off: int, color: Qt.GlobalColor, parent: 'SignalBar'):
        super().__init__()
        self.__bar = parent
        self.__name = name
        self.__num = num
        self.__off = off
        self.__color = color
        self.__label = SignalLabel(self.__bar.ctrl.lst)
        self.__label.setText(name)


class SignalLabelList(QListWidget):

    def __init__(self, parent: 'SignalCtrlWidget'):
        super().__init__(parent)


class ZoomButton(QPushButton):
    def __init__(self, txt: str, parent: 'ZoomButtonBox' = None):
        super().__init__(txt, parent)
        self.setContentsMargins(QMargins())  # not helps
        self.setFixedWidth(16)
        # self.setFlat(True)
        # TODO: squeeze


class ZoomButtonBox(QWidget):
    _b_zoom_in: ZoomButton
    _b_zoom_0: ZoomButton
    _b_zoom_out: ZoomButton

    def __init__(self, parent: 'SignalCtrlWidget'):
        super().__init__(parent)
        self._b_zoom_in = ZoomButton("+", self)
        self._b_zoom_0 = ZoomButton("=", self)
        self._b_zoom_out = ZoomButton("-", self)
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(QMargins())
        self.layout().addWidget(self._b_zoom_in)
        self.layout().addWidget(self._b_zoom_0)
        self.layout().addWidget(self._b_zoom_out)


class SignalCtrlWidget(QWidget):
    lst: SignalLabelList
    zbx: ZoomButtonBox

    def __init__(self, parent: 'SignalBar'):
        super().__init__(parent)
        self.lst = SignalLabelList(self)
        self.zbx = ZoomButtonBox(self)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.lst)
        self.layout().addWidget(self.zbx)


class SignalPlotWidget(QWidget):
    def __init__(self, parent: 'SignalBar'):
        super().__init__(parent)


class SignalBar(QWidget):
    sig: set[SignalSet]
    ctrl: SignalCtrlWidget
    plot_w: SignalPlotWidget
    plot: SignalPlot
    splitter: QSplitter

    def __init__(self, parent: 'SignalBarList'):
        super().__init__(parent)
        self.sig = set()
        self.__mk_widgets()
        self.__mk_layout()

    def __mk_widgets(self):
        self.ctrl = SignalCtrlWidget(self)
        self.plot_w = SignalPlotWidget(self)
        self.plot = SignalPlot(self.plot_w)

    def __mk_layout(self):
        self.setLayout(QVBoxLayout())
        self.splitter = QSplitter(Qt.Vertical, self)
        self.splitter.addWidget(self.ctrl)
        self.splitter.addWidget(self.plot_w)
        self.layout().addWidget(self.splitter)

    def add_sig(self, name: str, num: int, off: int, color: Qt.GlobalColor):
        sigset = SignalSet(name, num, off, color, self)
        self.sig.add(sigset)


class SignalBarList(QListWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setDragEnabled(True)

    def add_bar(self) -> SignalBar:
        # Note: QListWidgetItem cannot be parent
        self.setItemWidget(QListWidgetItem(self), bar := SignalBar(self))
        return bar


class MainWidget(QWidget):
    tb: TopBar
    cb: QWidget
    lst1: SignalBarList
    lst2: SignalBarList

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.__mk_widgets()
        self.__mk_layout()
        self.__set_data()

    def __mk_widgets(self):
        self.tb = TopBar(self)
        self.lst1 = SignalBarList(self)
        self.lst2 = SignalBarList(self)

    def __mk_layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tb)
        splitter = QSplitter(Qt.Vertical, self)
        splitter.setStyleSheet("QSplitter::handle{background: grey;}")
        splitter.addWidget(self.lst1)
        splitter.addWidget(self.lst2)
        self.layout().addWidget(splitter)

    def __set_data(self):
        for i, lst in enumerate((self.lst1, self.lst2)):
            for j in range(BARS):
                bar = lst.add_bar()
                continue
                bar.add_sig(
                    f"sig{i}/{j}",
                    random.randint(1, 5),
                    random.randint(0, SIN_SAMPLES - 1),
                    COLORS[random.randint(0, len(COLORS) - 1)]
                )


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
