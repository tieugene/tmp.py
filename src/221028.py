#!/usr/bin/env python3
"""Sample QTableWidget:
Лента: ribbon, band, lane, strip, set, bar
TODO:
- [x] TopBar
- [x] Col0 resize sync
- [ ] Signal join/move/unjoin (DnD)
- [ ] Signal hide/unhide
- [ ] HScroller
- [ ] Rerange:
  - [ ] x-scale
  - [ ] x-move
  - [ ] y-scale
  - [ ] y-stretch
  - [ ] y-move
- [ ] xPtr
IDEA: store signal pointer into Signal
"""
import math
import random
# 1. std
import sys
from dataclasses import dataclass

# 2. 3rd
from PyQt5.QtCore import Qt, QObject, QMargins, QRect, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPen, QColorConstants, QColor, QFont
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QWidget, QMainWindow, QVBoxLayout, QApplication, QSplitter, \
    QPushButton, QHBoxLayout, QTableWidget, QFrame, QHeaderView, QLabel, QScrollBar
from QCustomPlot2 import QCustomPlot, QCPGraph, QCPAxis

# x. const
BARS = 6  # Signal bars number (each table)
SIN_SAMPLES = 72  # 5°
SIG_WIDTH = 1.0  # signal width, s
LINE_CELL_SIZE = 3  # width ow VLine column / height of HLine row
BAR_HEIGHT = 48
COL0_WIDTH_INIT = 100
COL0_WIDTH_MIN = 50
PEN_NONE = QPen(QColor(255, 255, 255, 0))
PEN_ZERO = QPen(Qt.black)
COLORS = (Qt.black, Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.gray)
X_COORDS = [SIG_WIDTH / SIN_SAMPLES * i - SIG_WIDTH / 2 for i in range(SIN_SAMPLES+1)]


def y_coords(pnum: int = 1, off: int = 0) -> list[float]:
    """Create sinusoide.
    :param pnum: Periods number
    :param off: Offset (samples)
    :return: Y-coords
    """
    return [round(math.sin((i + off) / SIN_SAMPLES * 2 * math.pi * pnum), 3) for i in range(SIN_SAMPLES + 1)]


@dataclass
class Signal:
    num: int  # order number
    name: str
    pnum: int  # period number
    off: int  # offset (samples)
    color: QColorConstants


class TopBar(QWidget):

    class TopPlot(QCustomPlot):
        def __init__(self, parent: QWidget):
            super().__init__(parent)
            ar = self.axisRect(0)  # QCPAxisRect
            ar.setMinimumMargins(QMargins())  # the best
            ar.removeAxis(self.yAxis)
            ar.removeAxis(self.xAxis2)
            ar.removeAxis(self.yAxis2)
            self.xAxis.setTickLabelSide(QCPAxis.lsInside)
            self.xAxis.grid().setVisible(False)
            # self.xAxis.setTickLabels(True)
            # self.xAxis.setTicks(True)
            self.xAxis.setPadding(0)
            self.setFixedHeight(24)
            self.xAxis.setTickLabelFont(QFont('mono', 8))
            # data
            self.xAxis.setRange(X_COORDS[0], X_COORDS[-1])

    __label: QLabel
    __scale: TopPlot
    __stub: QScrollBar

    def __init__(self, parent: 'OscWindow'):
        super().__init__(parent)
        # widgets
        self.__label = QLabel("ms", self)
        self.__scale = self.TopPlot(self)
        self.__stub = QScrollBar(Qt.Vertical)
        # layout
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__label)
        self.layout().addWidget(self.__scale)
        self.layout().addWidget(self.__stub)
        # decorate
        # self.__label.setFrameShape(QFrame.Box)
        # self.__stub.setStyle(QCommonStyle())
        # squeeze
        self.__stub.setFixedHeight(0)
        # self.setContentsMargins(QMargins())
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)
        self.__label.setContentsMargins(QMargins())
        # init sizes
        self.__label.setFixedWidth(parent.col0_width + LINE_CELL_SIZE)
        # print(self.parent().metaObject().className())
        self.parent().signal_resize_col0.connect(self.__slot_resize_col0)

    def __slot_resize_col0(self, x: int):
        self.__label.setFixedWidth(x + LINE_CELL_SIZE)


class SignalLabel(QListWidgetItem):
    def __init__(self, parent: 'SignalLabelList' = None):
        super().__init__(parent)


class BarPlot(QCustomPlot):
    __bnum: int  # Bar number

    def __init__(self, bnum: int, parent):
        super().__init__(parent)
        self.__bnum = bnum
        self.__squeeze()
        self.yAxis.setBasePen(PEN_NONE)  # hack
        self.yAxis.grid().setZeroLinePen(PEN_ZERO)
        self.xAxis.grid().setZeroLinePen(PEN_ZERO)
        self.xAxis.setRange(X_COORDS[0], X_COORDS[-1])
        self.yAxis.setRange(-1.1, 1.1)

    def __squeeze(self):
        ar = self.axisRect(0)  # QCPAxisRect
        ar.setMinimumMargins(QMargins())  # the best
        ar.removeAxis(self.xAxis2)
        ar.removeAxis(self.yAxis2)
        # self.yAxis.setVisible(False)  # or cp.graph().valueAxis()
        self.yAxis.setTickLabels(False)
        self.yAxis.setTicks(False)
        self.yAxis.setPadding(0)
        self.yAxis.ticker().setTickCount(1)  # the only z-line
        self.xAxis.setTickLabels(False)
        self.xAxis.setTicks(False)
        self.xAxis.setPadding(0)


class SignalSuit(QObject):
    __signal: Signal
    __label: SignalLabel
    __graph: QCPGraph

    def __init__(self, signal: Signal, ctrl: 'BarCtrl', plot: BarPlot):
        super().__init__()
        self.__signal = signal
        self.__label = SignalLabel(ctrl.lst)
        self.__label.setText(f"{signal.name}\n{signal.pnum}/{signal.off}")
        self.__graph = plot.addGraph()
        self.__graph.setData(X_COORDS, y_coords(signal.pnum, signal.off), True)
        self.__graph.setPen(QPen(signal.color))


class SignalLabelList(QListWidget):

    def __init__(self, parent: 'BarCtrl'):
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

    def __init__(self, parent: 'BarCtrl'):
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


class BarCtrl(QWidget):
    __bnum: int  # Bar order number in parent table
    lst: SignalLabelList
    zbx: ZoomButtonBox

    def __init__(self, bnum: int, parent):
        super().__init__(parent)
        self.__bnum = bnum
        self.lst = SignalLabelList(self)
        self.zbx = ZoomButtonBox(self)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.lst)
        self.layout().addWidget(self.zbx)
        self.layout().setContentsMargins(QMargins())


class HLine(QFrame):  # TODO: incapsulate into SignalBarTable
    __bnum: int

    def __init__(self, bnum: int, parent=None):
        """Parents: QWidget<OscWindow"""
        super().__init__(parent)
        self.__bnum = bnum
        self.setGeometry(QRect(0, 0, 0, 0))  # size is not the matter
        self.setFrameShape(QFrame.HLine)
        self.setCursor(Qt.SplitVCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """accepted() == True, y() = Δy"""
        (tbl := self.parent().parent()).setRowHeight(self.__bnum * 2, tbl.rowHeight(self.__bnum * 2) + event.y())


class VLine(QFrame):  # TODO: incapsulate into SignalBarTable
    __oscwin: 'OscWindow'

    def __init__(self, oscwin: 'OscWindow', parent=None):
        super().__init__(parent)
        self.__oscwin = oscwin
        self.setGeometry(QRect(0, 0, 0, 0))  # size is not the matter
        self.setFrameShape(QFrame.VLine)
        self.setCursor(Qt.SplitHCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """accepted() == True, x() = Δx.
        :note: parents: QWidget.SignalBarTable.QSplitter.OscWindow
        """
        # (tbl := self.parent().parent()).setColumnWidth(0, tbl.columnWidth(0) + event.x())
        self.__oscwin.resize_col0(event.x())


class SignalBarTable(QTableWidget):
    __oscwin: 'OscWindow'

    def __init__(self, oscwin: 'OscWindow', parent: QWidget = None):
        super().__init__(parent)
        self.__oscwin = oscwin
        self.setColumnCount(3)
        self.horizontalHeader().setMinimumSectionSize(1)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        self.setColumnWidth(0, self.__oscwin.col0_width)
        self.setColumnWidth(1, LINE_CELL_SIZE)
        self.verticalHeader().setMinimumSectionSize(1)
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # not helps
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # not helps
        self.setShowGrid(False)
        self.setDragEnabled(True)
        # signal/slot
        self.__oscwin.signal_resize_col0.connect(self.__slot_resize_col0)

    def __slot_resize_col0(self, x: int):
        self.setColumnWidth(0, x)

    def bar_insert(self, bnum: int = -1):
        if bnum < 0 or bnum > (self.rowCount() // 2):
            bnum = self.rowCount() // 2
        row_sig = bnum * 2
        row_spl = row_sig + 1
        # signal
        self.insertRow(row_sig)
        self.setCellWidget(row_sig, 0, BarCtrl(bnum, self))
        self.setCellWidget(row_sig, 1, VLine(self.__oscwin, self))
        self.setCellWidget(row_sig, 2, BarPlot(bnum, self))
        self.setRowHeight(row_sig, BAR_HEIGHT)
        # h-splitter
        self.insertRow(row_spl)
        self.setCellWidget(row_spl, 0, HLine(bnum, self))
        self.setCellWidget(row_spl, 1, HLine(bnum, self))
        self.setCellWidget(row_spl, 2, HLine(bnum, self))
        self.setRowHeight(row_spl, LINE_CELL_SIZE)

    def sig_add(self, bnum: int, signal: Signal):
        sigsuit = SignalSuit(signal, self.cellWidget(bnum * 2, 0), self.cellWidget(bnum * 2, 2))

    def sig_del(self):
        """Remove signal from bar.
        """
        ...


class OscWindow(QWidget):
    tb: TopBar
    cb: QWidget
    lst1: SignalBarTable
    lst2: SignalBarTable
    col0_width = COL0_WIDTH_INIT
    signal_resize_col0 = pyqtSignal(int)

    def __init__(self, data: list[Signal], parent: QMainWindow):
        super().__init__(parent)
        self.__mk_widgets()
        self.__mk_layout()
        self.__set_data(data)

    def __mk_widgets(self):
        self.tb = TopBar(self)
        self.lst1 = SignalBarTable(self)
        self.lst2 = SignalBarTable(self)

    def __mk_layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tb)
        splitter = QSplitter(Qt.Vertical, self)
        splitter.addWidget(self.lst1)
        splitter.addWidget(self.lst2)
        self.layout().addWidget(splitter)
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)

    def __set_data(self, data: list[Signal]):
        def __set_data_one(__tbl: SignalBarTable, __data: list[Signal]):
            for __j, __sig in enumerate(__data):
                __tbl.bar_insert(__j)
                __tbl.sig_add(__j, __sig)
        n0 = len(data) // 2
        __set_data_one(self.lst1, data[:n0])
        __set_data_one(self.lst2, data[n0:])

    def resize_col0(self, dx: int):
        if self.col0_width + dx > COL0_WIDTH_MIN:
            self.col0_width += dx
            self.signal_resize_col0.emit(self.col0_width)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        data = [Signal(
            num=i,
            name=f"sig{i}",
            pnum=random.randint(1, 5),
            off=random.randint(0, SIN_SAMPLES - 1),
            color=COLORS[random.randint(0, len(COLORS) - 1)]
        ) for i in range(BARS)]
        self.setCentralWidget(OscWindow(data, self))


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
