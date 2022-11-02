#!/usr/bin/env python3
"""Sample QTableWidget:
Лента: ribbon, band, lane, strip, set, bars
TODO:
- [x] TopBar
- [x] Col0 resize sync
- [ ] Signal join/move/unjoin (DnD)
  - [ ] Drop enable/disable on the fly
- [ ] Hide/unhide
  - [ ] Bar
  - [ ] Signal
- [ ] HScroller
- [ ] Rerange:
  - [ ] x-scale
  - [ ] x-move
  - [ ] y-scale
  - [ ] y-stretch
  - [ ] y-move
- [ ] xPtr
IDEA: store signals pointer into Signal
"""
# 1. std
from typing import Tuple, Optional
import sys
from dataclasses import dataclass
import math
import random

# 2. 3rd
from PyQt5.QtCore import Qt, QObject, QMargins, QRect, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPen, QColorConstants, QColor, QFont, QDropEvent
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QWidget, QMainWindow, QVBoxLayout, QApplication, QSplitter, \
    QPushButton, QHBoxLayout, QTableWidget, QFrame, QHeaderView, QLabel, QScrollBar, QGridLayout
from QCustomPlot2 import QCustomPlot, QCPGraph, QCPAxis

# x. const
BARS = 8  # Signal bars number (each table)
SIN_SAMPLES = 72  # 5°
SIG_WIDTH = 1.0  # signals width, s
LINE_CELL_SIZE = 3  # width ow VLine column / height of HLine row
BAR_HEIGHT = 48
COL_CTRL_WIDTH_INIT = 100
COL_CTRL_WIDTH_MIN = 50
PEN_NONE = QPen(QColor(255, 255, 255, 0))
PEN_ZERO = QPen(Qt.black)
COLORS = (Qt.black, Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.gray)
X_COORDS = [SIG_WIDTH / SIN_SAMPLES * i - SIG_WIDTH / 2 for i in range(SIN_SAMPLES + 1)]


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
        self.__slot_resize_col_ctrl(parent.col_ctrl_width)
        self.parent().signal_resize_col_ctrl.connect(self.__slot_resize_col_ctrl)

    def __slot_resize_col_ctrl(self, x: int):
        self.__label.setFixedWidth(x + LINE_CELL_SIZE)


class SignalLabel(QListWidgetItem):
    def __init__(self, parent: 'SignalLabelList' = None):
        super().__init__(parent)


class SignalLabelList(QListWidget):

    def __init__(self, parent: 'BarCtrlWidget'):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.itemClicked.connect(self.__slot_item_clicked)

    def __slot_item_clicked(self, _):
        """Deselect item on mouse up"""
        self.clearSelection()


class ZoomButton(QPushButton):
    def __init__(self, txt: str, parent: 'ZoomButtonBox'):
        super().__init__(txt, parent)
        self.setContentsMargins(QMargins())  # not helps
        self.setFixedWidth(16)
        # self.setFlat(True)
        # TODO: squeeze


class ZoomButtonBox(QWidget):
    _b_zoom_in: ZoomButton
    _b_zoom_0: ZoomButton
    _b_zoom_out: ZoomButton

    def __init__(self, parent: 'BarCtrlWidget'):
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


class VLine(QFrame):  # TODO: hide into SignalBarTable
    __oscwin: 'OscWindow'

    def __init__(self, oscwin: 'OscWindow'):
        super().__init__()
        self.__oscwin = oscwin
        self.setGeometry(QRect(0, 0, 0, 0))  # size is not the matter
        self.setFrameShape(QFrame.VLine)
        self.setCursor(Qt.SplitHCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """accepted() == True, x() = Δx."""
        self.__oscwin.resize_col_ctrl(event.x())


class HLine(QFrame):  # TODO: hide into SignalBarTable
    __parent: 'BarCtrlWidget'

    def __init__(self, parent: 'BarCtrlWidget'):
        super().__init__()
        self.__parent = parent
        self.setGeometry(QRect(0, 0, 0, 0))  # size is not the matter
        self.setFrameShape(QFrame.HLine)
        self.setCursor(Qt.SplitVCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """accepted() == True, y() = Δy."""
        (b := self.__parent.bar).table.setRowHeight(b.row, b.table.rowHeight(b.row) + event.y())


class BarCtrlWidget(QWidget):
    bar: 'SignalBar'
    lst: SignalLabelList
    zbx: ZoomButtonBox

    def __init__(self, bar: 'SignalBar'):
        super().__init__()  # parent will be QWidget
        self.bar = bar
        self.lst = SignalLabelList(self)
        self.zbx = ZoomButtonBox(self)
        # layout
        layout = QGridLayout()
        layout.addWidget(QLabel('↕', self), 0, 0)
        layout.addWidget(self.lst, 0, 1)
        layout.addWidget(self.zbx, 0, 2)
        layout.addWidget(VLine(self.bar.table.oscwin), 0, 3)
        layout.addWidget(HLine(self), 1, 0, 1, -1)
        self.setLayout(layout)
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Deselect item on mouse up"""
        super().mouseReleaseEvent(event)
        self.bar.table.clearSelection()

    def sig_add(self) -> SignalLabel:
        return SignalLabel(self.lst)

    def sig_del(self, i: int):
        label = self.lst.takeItem(i)
        del label


class BarPlot(QCustomPlot):
    def __init__(self, parent: 'BarPlotWidget'):
        super().__init__(parent)
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


class BarPlotWidget(QWidget):
    # TODO: add_signal
    bar: 'SignalBar'
    plot: BarPlot

    def __init__(self, bar: 'SignalBar'):
        super().__init__()
        self.bar = bar
        self.plot = BarPlot(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.plot)
        self.layout().addWidget(HLine(self))
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Deselect item on mouse up"""
        super().mouseReleaseEvent(event)
        self.bar.table.clearSelection()

    def sig_add(self) -> QCPGraph:
        return self.plot.addGraph()

    def sig_del(self, gr: QCPGraph):
        self.plot.removeGraph(gr)


class SignalSuit(QObject):
    __signal: Signal
    __bar: Optional['SignalBar']
    num: Optional[int]
    __label: SignalLabel
    __graph: QCPGraph

    def __init__(self, signal: Signal):
        super().__init__()
        self.__signal = signal
        self.__bar = None
        self.num = None

    def embed(self, bar: 'SignalBar', num: int):
        self.__bar = bar
        self.num = num
        self.__label = self.__bar.ctrl.sig_add()
        self.__label.setText(f"{self.__signal.name}\n{self.__signal.pnum}/{self.__signal.off}")
        self.__graph = self.__bar.gfx.sig_add()
        self.__graph.setData(X_COORDS, y_coords(self.__signal.pnum, self.__signal.off), True)
        self.__graph.setPen(QPen(self.__signal.color))

    def detach(self):
        self.__bar.ctrl.sig_del(self.num)
        self.__bar.gfx.sig_del(self.__graph)
        self.num = None
        self.__bar = None


class SignalBar(QObject):
    table: 'SignalBarTable'
    row: int
    signals: list[SignalSuit]
    ctrl: BarCtrlWidget
    gfx: BarPlotWidget

    def __init__(self, table: 'SignalBarTable', row: int = -1):
        super().__init__()
        if not (0 <= row < table.rowCount()):
            row = table.rowCount()
        self.table = table
        self.row = row
        self.signals = list()
        self.ctrl = BarCtrlWidget(self)
        self.gfx = BarPlotWidget(self)
        self.table.bars.insert(self.row, self)
        self.table.insertRow(self.row)
        self.table.setCellWidget(self.row, 0, self.ctrl)
        self.table.setCellWidget(self.row, 1, self.gfx)

    def suicide(self):
        del self.table.bars[self.row]
        self.table.removeCellWidget(self.row, 0)
        self.table.removeCellWidget(self.row, 1)
        self.table.removeRow(self.row)
        self.ctrl.close()
        self.gfx.close()
        self.deleteLater()

    def sig_add(self, ss: SignalSuit):
        ss.embed(self, len(self.signals))
        self.signals.append(ss)

    def sig_move(self, i: int, other_bar: 'SignalBar'):
        ss = self.signals[i]
        del self.signals[i]
        ss.detach()
        other_bar.sig_add(ss)
        if self.signals:
            for i, ss in enumerate(self.signals):
                ss.num = i
        else:
            self.suicide()

    def move(self, other_table: 'SignalBarTable', other_row: int):  # TODO:
        ...


class SignalBarTable(QTableWidget):
    oscwin: 'OscWindow'
    bars: list[SignalBar]

    def __init__(self, oscwin: 'OscWindow'):
        super().__init__()  # Parent will be QSplitter
        self.oscwin = oscwin
        self.setColumnCount(2)
        self.bars = list()
        # self.horizontalHeader().setMinimumSectionSize(1)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        self.__slot_resize_col_ctrl(self.oscwin.col_ctrl_width)
        # self.verticalHeader().setMinimumSectionSize(1)
        self.verticalHeader().hide()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setShowGrid(False)
        # self.setSelectionMode(self.SingleSelection)
        # self.setSelectionBehavior(self.SelectRows)
        # DnD
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        # self.setDragDropMode(self.DragDrop)
        # signals/slot
        self.oscwin.signal_resize_col_ctrl.connect(self.__slot_resize_col_ctrl)

    def insertRow(self, row: int):
        super().insertRow(row)
        for i in range(row + 1, len(self.bars)):
            self.bars[i].row = i

    def removeRow(self, row: int):
        super().removeRow(row)
        for i in range(row, len(self.bars)):
            self.bars[i].row = i

    def dropEvent(self, event: QDropEvent):
        # RTFM drag{Enter,Move,Leave}Event
        def _drop_on(__evt: QDropEvent) -> Tuple[int, bool]:
            __dip = self.dropIndicatorPosition()  # 0: on row, 3: out
            __index = self.indexAt(__evt.pos())  # isValid: T: on row, F: out
            if not __index.isValid():  # below last
                return self.rowCount(), False
            if __dip == self.AboveItem:
                return __index.row(), False
            elif __dip == self.BelowItem:
                return __index.row() + 1, False
            elif __dip == self.OnItem:
                return __index.row(), True
            else:
                return -1, False

        def _t_ins_i(__src_row_num: int, __dst_row_num: int):
            """In-table row move"""
            self.insertRow(__dst_row_num)  # FIXME: bar_add
            self.setRowHeight(__dst_row_num, self.rowHeight(__src_row_num))
            if __src_row_num > __dst_row_num:
                __src_row_num += 1
            # copy widgets
            self.setCellWidget(__dst_row_num, 0, self.cellWidget(__src_row_num, 0))
            self.setCellWidget(__dst_row_num, 1, self.cellWidget(__src_row_num, 1))

        def _s_ovr(__src_list: SignalLabelList, __src_row_num: int, __dst_row_num: int):
            __src_list.parent().bar.sig_move(__src_row_num, self.bars[__dst_row_num])

        if event.isAccepted():
            super().dropEvent(event)
            return
        event.accept()
        event.setDropAction(Qt.IgnoreAction)  # default action
        dst_row_num, over = _drop_on(event)
        if dst_row_num < 0:
            print("DnD: unknown dest row")
            return
        src_object = event.source()  # SignalBarTable/SignalLabelList
        if isinstance(src_object, SignalBarTable):  # Bar.
            if over:  # Bar.Ovr
                print("Bar join not supported", file=sys.stderr)
            else:  # Bar.Ins
                src_row_num: int = src_object.selectedIndexes()[0].row()
                if src_object == self:  # Bar.Ins.i
                    if (dst_row_num - src_row_num) in {0, 1}:
                        print("Moving bars nearby doesn't make sense", file=sys.stderr)
                    else:
                        # print("Bar.Ins.i", dst_row_num)
                        _t_ins_i(src_row_num, dst_row_num)
                        event.setDropAction(Qt.MoveAction)
                else:  # Bar.Ins.x
                    print("Bar.Ins.x", dst_row_num)
                    # _t_b2n_x(src_object, src_row_num, dst_row_num)
                    # event.setDropAction(Qt.MoveAction)
            src_object.clearSelection()
        elif isinstance(src_object, SignalLabelList):  # Sig.
            # Note: MoveAction clears all of listwidget on sig move
            src_row_num: int = src_object.selectedIndexes()[0].row()
            if over:  # Sig.Ovr
                if src_object.parent().bar.table == self and src_object.parent().bar.row == dst_row_num:
                    print("Join signals to itself doesn't make sense", file=sys.stderr)
                else:
                    # print("Sig.Ovr", dst_row_num)
                    _s_ovr(src_object, src_row_num, dst_row_num)
                    # event.setDropAction(Qt.MoveAction)
            else:  # sig.Ins
                if src_object.count() == 1:
                    print("Unjoin single signals doesn't make sense", file=sys.stderr)
                else:
                    print("Sig.Ins", dst_row_num)
                    # _s_b2n(src_object, src_row_num, dst_row_num)
                    # #event.setDropAction(Qt.MoveAction)
            src_object.clearSelection()
        else:
            print("Unknown src object: %s" % src_object.metaObject().className(), file=sys.stderr)

    def __slot_resize_col_ctrl(self, x: int):
        self.setColumnWidth(0, x)

    def bar_insert(self, row: int = -1) -> SignalBar:
        return SignalBar(self, row)


class OscWindow(QWidget):
    tb: TopBar
    cb: QWidget
    lst1: SignalBarTable
    lst2: SignalBarTable
    col_ctrl_width = COL_CTRL_WIDTH_INIT
    signal_resize_col_ctrl = pyqtSignal(int)

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
                bar = __tbl.bar_insert(__j)
                __tbl.setRowHeight(bar.row, BAR_HEIGHT)
                bar.sig_add(SignalSuit(__sig))

        n0 = len(data) // 2
        __set_data_one(self.lst1, data[:n0])
        __set_data_one(self.lst2, data[n0:])

    def resize_col_ctrl(self, dx: int):
        if self.col_ctrl_width + dx > COL_CTRL_WIDTH_MIN:
            self.col_ctrl_width += dx
            self.signal_resize_col_ctrl.emit(self.col_ctrl_width)


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
