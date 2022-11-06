#!/usr/bin/env python3
"""Sample iOsc.py prototype (new style, started 20221028):
- [ ] FIXME: Row selection (idea: drag anchor only)
  + [x] Highlight: ovr/ins (mime)
  + [ ] Use QMimeType (table, bar/signal)
  + [ ] Multilevel DragMove: src type > State changed (row, over)
  + [ ] SignalLabelList.Item too
- [ ] FIXME: DnD: replot src and dst after ...
- [ ] FIXME: Hide full YScroller, XScroller, RStub
- [ ] FIXME: Glitches (x-scale)
- note: item.row/num == item.index().row()
"""
# 1. std
from typing import Tuple, Optional
from dataclasses import dataclass
import sys
import math
import random
# 2. 3rd
from PyQt5.QtCore import Qt, QObject, QMargins, QRect, pyqtSignal, QPoint, QMimeData
from PyQt5.QtGui import QMouseEvent, QPen, QColorConstants, QColor, QFont, QDropEvent, QDragMoveEvent, QResizeEvent, \
    QPixmap, QDrag, QDragEnterEvent, QPainter
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QWidget, QMainWindow, QVBoxLayout, QApplication, QSplitter, \
    QPushButton, QHBoxLayout, QTableWidget, QFrame, QHeaderView, QLabel, QScrollBar, QGridLayout, QMenu, QAction
from QCustomPlot2 import QCustomPlot, QCPGraph, QCPAxis, QCPAxisTickerFixed, QCPScatterStyle

# x. const
# - user defined
BARS = 8  # Signals number
SIN_SAMPLES = 360  # Samples per signal (72 = 5°)
SIG_WIDTH = 2.0  # Signals width, s
# - hardcoded
LINE_CELL_SIZE = 3  # width of VLine column / height of HLine row
BAR_HEIGHT = 48  # Initial SignalBarTable row height
COL_CTRL_WIDTH_INIT = 100  # Initial BarCtrlWidget column width
COL_CTRL_WIDTH_MIN = 50  # Minimal BarCtrlWidget column width
PEN_NONE = QPen(QColor(255, 255, 255, 0))
PEN_ZERO = QPen(Qt.black)
COLORS = (Qt.black, Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.gray)
ZOOM_Y_MAX = 100  # Max Y-zoom factor
YSCROLL_WIDTH = ZOOM_Y_MAX * 100  # Constant YScroller width, units
X_PX_WIDTH_uS = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000)  # Px widhts, μs
SCATTER_BOUND_PX = 10  # limit of sample interval (px) to switch scatter style


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
        signal_width_changed = pyqtSignal(int)

        def __init__(self, parent: 'TopBar'):
            super().__init__(parent)
            ar = self.axisRect(0)  # QCPAxisRect
            ar.setMinimumMargins(QMargins())  # the best
            ar.removeAxis(self.yAxis)
            ar.removeAxis(self.xAxis2)
            ar.removeAxis(self.yAxis2)
            self.xAxis.setTickLabelSide(QCPAxis.lsInside)
            self.xAxis.grid().setVisible(False)
            self.xAxis.setTicker(QCPAxisTickerFixed())
            # self.xAxis.setTickLabels(True)  # default
            # self.xAxis.setTicks(True)  # default
            self.xAxis.setPadding(0)
            self.xAxis.setTickLabelFont(QFont('mono', 8))
            self.setFixedHeight(24)
            # data
            x_coords = parent.parent().x_coords
            self.xAxis.setRange(x_coords[0], x_coords[-1])
            self.__slot_retick()
            parent.parent().signal_x_zoom.connect(self.__slot_retick)

        def resizeEvent(self, event: QResizeEvent):
            super().resizeEvent(event)
            if event.oldSize().width() != (w := event.size().width()):
                self.signal_width_changed.emit(w)

        def slot_rerange(self):
            oscwin = self.parent().parent()
            x_coords = oscwin.x_coords
            x_width = x_coords[-1] - x_coords[0]
            self.xAxis.setRange(
                x_coords[0] + oscwin.hs.norm_min * x_width,
                x_coords[0] + oscwin.hs.norm_max * x_width,
            )

        def slot_rerange_force(self):
            self.slot_rerange()
            self.replot()

        def __slot_retick(self):
            self.xAxis.ticker().setTickStep(X_PX_WIDTH_uS[self.parent().parent().x_zoom] / 10)
            self.replot()

    class RStub(QScrollBar):
        def __init__(self, parent: 'TopBar' = None):
            super().__init__(Qt.Vertical, parent)
            self.setFixedHeight(0)

    __label: QLabel
    plot: TopPlot

    def __init__(self, parent: 'OscWindow'):
        super().__init__(parent)
        # widgets
        self.__label = QLabel("ms", self)
        self.plot = self.TopPlot(self)
        # layout
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.__label)
        self.layout().addWidget(self.plot)
        self.layout().addWidget(self.RStub())
        self.layout().addWidget(self.RStub())
        # decorate
        # self.__label.setFrameShape(QFrame.Box)
        # self.__stub.setStyle(QCommonStyle())
        # squeeze
        # self.setContentsMargins(QMargins())
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)
        self.__label.setContentsMargins(QMargins())
        # init sizes
        self.__slot_resize_col_ctrl(parent.col_ctrl_width)
        self.parent().signal_resize_col_ctrl.connect(self.__slot_resize_col_ctrl)

    def __slot_resize_col_ctrl(self, x: int):
        self.__label.setFixedWidth(x + LINE_CELL_SIZE)


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
    class Anchor(QLabel):
        def __init__(self, parent: 'BarCtrlWidget'):
            super().__init__(parent)
            self.setText('↕')
            self.setCursor(Qt.PointingHandCursor)

        def mousePressEvent(self, event: QMouseEvent):
            self.__start_drag(event.pos())

        def __start_drag(self, pos: QPoint):
            def _mk_icon() -> QPixmap:
                __txt = self.parent().bar.signals[0].signal.name
                __pix = QPixmap(64, 16)  # w, h; TODO: width == current SignalLabelList.width()
                __pix.fill(Qt.transparent)  # TODO: border
                __painter = QPainter(__pix)
                __painter.setFont(QFont('mono', 8))
                __painter.setPen(QPen(Qt.black))
                __painter.drawText(0, 8, __txt)  # x, y (baseline)
                return __pix

            def _mk_mime() -> QMimeData:
                bar: SignalBar = self.parent().bar
                return bar.table.mimeData([bar.table.item(bar.row, 0)])

            drag = QDrag(self)
            drag.setPixmap(_mk_icon())
            drag.setMimeData(_mk_mime())
            drag.setHotSpot(pos)
            drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)

    class SignalLabelList(QListWidget):
        class Item(QListWidgetItem):
            ss: 'SignalSuit'

            def __init__(self, ss: 'SignalSuit', parent: 'BarCtrlWidget.SignalLabelList'):
                super().__init__(parent)
                self.ss = ss
                # self.setCursor(Qt.PointingHandCursor)  # n/a

        def __init__(self, parent: 'BarCtrlWidget'):
            super().__init__(parent)
            self.setDragEnabled(True)
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.__slot_context_menu)
            self.itemClicked.connect(self.__slot_item_clicked)

        def __slot_item_clicked(self, _):
            """Deselect item on mouse up"""
            self.clearSelection()

        def __slot_context_menu(self, point: QPoint):
            item: BarCtrlWidget.SignalLabelList.Item = self.itemAt(point)
            if not item:
                return
            context_menu = QMenu()
            action_sig_hide = context_menu.addAction("Hide")
            chosen_action = context_menu.exec_(self.mapToGlobal(point))
            if chosen_action == action_sig_hide:
                item.ss.set_hidden(True)

        @property
        def selected_row(self) -> int:
            return self.selectedIndexes()[0].row()

    class ZoomButtonBox(QWidget):
        class ZoomButton(QPushButton):
            def __init__(self, txt: str, parent: 'ZoomButtonBox'):
                super().__init__(txt, parent)
                self.setContentsMargins(QMargins())  # not helps
                self.setFixedWidth(16)
                self.setFlat(True)
                self.setCursor(Qt.PointingHandCursor)

        __b_zoom_in: ZoomButton
        __b_zoom_0: ZoomButton
        __b_zoom_out: ZoomButton

        def __init__(self, parent: 'BarCtrlWidget'):
            super().__init__(parent)
            self.__b_zoom_in = self.ZoomButton("+", self)
            self.__b_zoom_0 = self.ZoomButton("⚬", self)
            self.__b_zoom_out = self.ZoomButton("-", self)
            self.setLayout(QVBoxLayout())
            self.layout().setSpacing(0)
            self.layout().setContentsMargins(QMargins())
            self.layout().addWidget(self.__b_zoom_in)
            self.layout().addWidget(self.__b_zoom_0)
            self.layout().addWidget(self.__b_zoom_out)
            self.__update_buttons()
            self.__b_zoom_in.clicked.connect(self.__slot_zoom_in)
            self.__b_zoom_0.clicked.connect(self.__slot_zoom_0)
            self.__b_zoom_out.clicked.connect(self.__slot_zoom_out)

        def __slot_zoom_in(self):
            self.__slot_zoom(1)

        def __slot_zoom_out(self):
            self.__slot_zoom(-1)

        def __slot_zoom_0(self):
            self.__slot_zoom(0)

        def __slot_zoom(self, dy: int):
            self.parent().bar.zoom_dy(dy)
            self.__update_buttons()

        def __update_buttons(self):
            z = self.parent().bar.zoom_y
            self.__b_zoom_in.setEnabled(z < 1000)
            self.__b_zoom_0.setEnabled(z > 1)
            self.__b_zoom_out.setEnabled(z > 1)

    class VLine(QFrame):
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

    bar: 'SignalBar'
    anc: Anchor
    lst: SignalLabelList
    zbx: ZoomButtonBox

    def __init__(self, bar: 'SignalBar'):
        super().__init__()  # parent will be QWidget
        self.bar = bar
        self.anc = self.Anchor(self)
        self.lst = self.SignalLabelList(self)
        self.zbx = self.ZoomButtonBox(self)
        # layout
        layout = QGridLayout()
        layout.addWidget(self.anc, 0, 0)
        layout.addWidget(self.lst, 0, 1)
        layout.addWidget(self.zbx, 0, 2)
        layout.addWidget(self.VLine(self.bar.table.oscwin), 0, 3)
        layout.addWidget(HLine(self), 1, 0, 1, -1)
        self.setLayout(layout)
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)

    def mouseReleaseEvent(self, event: QMouseEvent):  # FIXME: not need
        """Deselect item on mouse up"""
        super().mouseReleaseEvent(event)
        self.bar.table.clearSelection()

    def sig_add(self, ss: 'SignalSuit') -> SignalLabelList.Item:
        return self.SignalLabelList.Item(ss, self.lst)

    def sig_del(self, i: int):
        self.lst.takeItem(i)


class BarPlotWidget(QWidget):
    class YZLabel(QLabel):
        def __init__(self, parent: 'BarPlotWidget'):
            super().__init__(parent)
            self.setStyleSheet("QLabel { background-color : red; color : rgba(255,255,255,255) }")
            self.__slot_zoom_changed()
            parent.bar.signal_zoom_y_changed.connect(self.__slot_zoom_changed)

        def __slot_zoom_changed(self):
            z = self.parent().bar.zoom_y
            if z == 1:
                self.hide()
            else:
                if self.isHidden():
                    self.show()
                self.setText(f"×{z}")
                self.adjustSize()

    class BarPlot(QCustomPlot):
        __y_min: float
        __y_max: float

        def __init__(self, parent: 'BarPlotWidget'):
            super().__init__(parent)
            self.__y_min = -1.1  # hack
            self.__y_max = 1.1  # hack
            self.__squeeze()
            self.__decorate()
            self.yAxis.setRange(self.__y_min, self.__y_max)
            # x_coords = parent.bar.table.oscwin.x_coords
            # self.xAxis.setRange(x_coords[0], x_coords[-1])
            parent.bar.table.oscwin.hs.valueChanged.connect(self.__slot_rerange_x_force)
            parent.bar.table.oscwin.hs.signal_update_plots.connect(self.__slot_rerange_x)
            parent.bar.table.oscwin.signal_x_zoom.connect(self.__slot_retick)

        @property
        def __y_width(self) -> float:
            return self.__y_max - self.__y_min

        def __squeeze(self):
            ar = self.axisRect(0)  # QCPAxisRect
            ar.setMinimumMargins(QMargins())  # the best
            ar.removeAxis(self.xAxis2)
            ar.removeAxis(self.yAxis2)
            # y
            # self.yAxis.setVisible(False)  # or cp.graph().valueAxis()
            self.yAxis.setTickLabels(False)
            self.yAxis.setTicks(False)
            self.yAxis.setPadding(0)
            self.yAxis.ticker().setTickCount(1)  # the only z-line
            # x
            self.xAxis.setTicker(QCPAxisTickerFixed())
            self.xAxis.setTickLabels(False)
            self.xAxis.setTicks(False)
            self.xAxis.setPadding(0)
            self.__slot_retick()

        def __decorate(self):
            self.yAxis.setBasePen(PEN_NONE)  # hack
            self.yAxis.grid().setZeroLinePen(PEN_ZERO)
            self.xAxis.grid().setZeroLinePen(PEN_ZERO)

        def slot_rerange_y(self, _: int):
            """Refresh plot on YScroller move"""
            ys: QScrollBar = self.parent().ys
            y_min = self.__y_min + self.__y_width * ys.y_norm_min
            y_max = self.__y_min + self.__y_width * ys.y_norm_max
            self.yAxis.setRange(y_min, y_max)
            self.replot()

        def __slot_rerange_x(self):
            oscwin = self.parent().bar.table.oscwin
            x_coords = oscwin.x_coords
            x_width = x_coords[-1] - x_coords[0]
            self.xAxis.setRange(
                x_coords[0] + oscwin.hs.norm_min * x_width,
                x_coords[0] + oscwin.hs.norm_max * x_width,
            )

        def __slot_rerange_x_force(self):
            self.__slot_rerange_x()
            self.replot()

        def __slot_retick(self):
            self.xAxis.ticker().setTickStep(X_PX_WIDTH_uS[self.parent().bar.table.oscwin.x_zoom] / 10)
            self.replot()

    class YScroller(QScrollBar):
        """Main idea:
        - Constant predefined width (in units; max)
        - Dynamic page (max..min for x1..xMax)
        """

        def __init__(self, parent: 'BarPlotWidget'):
            super().__init__(Qt.Vertical, parent)
            self.__slot_zoom_changed()
            parent.bar.signal_zoom_y_changed.connect(self.__slot_zoom_changed)

        @property
        def y_norm_min(self) -> float:
            """Normalized (0..1) minimal window position"""
            return 1 - (self.value() + self.pageStep()) / YSCROLL_WIDTH

        @property
        def y_norm_max(self) -> float:
            """Normalized (0..1) maximal window position"""
            return 1 - self.value() / YSCROLL_WIDTH

        def __slot_zoom_changed(self):
            z = self.parent().bar.zoom_y
            if z == 1:
                self.setPageStep(YSCROLL_WIDTH)
                self.setMaximum(0)
                self.setValue(0)  # note: exact in this order
            else:
                v0 = self.value()
                p0 = self.pageStep()
                p1 = round(YSCROLL_WIDTH / z)
                self.setPageStep(p1)
                self.setMaximum(YSCROLL_WIDTH - p1)
                self.setValue(v0 + round((p0 - p1) / 2))

    bar: 'SignalBar'
    yzlabel: YZLabel
    plot: BarPlot
    ys: YScroller

    def __init__(self, bar: 'SignalBar'):
        super().__init__()
        self.bar = bar
        self.plot = BarPlotWidget.BarPlot(self)
        self.ys = self.YScroller(self)
        self.yzlabel = self.YZLabel(self)
        layout = QGridLayout()
        layout.addWidget(self.plot, 0, 0)
        layout.addWidget(self.ys, 0, 1)
        layout.addWidget(HLine(self), 1, 0, 1, -1)
        self.setLayout(layout)
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)
        # parent.bar.signal_zoom_y_changed.connect(self.__update_buttons)
        self.ys.valueChanged.connect(self.plot.slot_rerange_y)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Deselect item on mouse up"""
        super().mouseReleaseEvent(event)
        self.bar.table.clearSelection()

    def sig_add(self) -> QCPGraph:
        return self.plot.addGraph()

    def sig_del(self, gr: QCPGraph):
        self.plot.removeGraph(gr)


class SignalSuit(QObject):
    __oscwin: 'OscWindow'
    signal: Signal
    __bar: Optional['SignalBar']
    num: Optional[int]
    __label: Optional[BarCtrlWidget.SignalLabelList.Item]
    __graph: Optional[QCPGraph]
    hidden: bool

    def __init__(self, signal: Signal, oscwin: 'OscWindow'):
        super().__init__()
        self.__oscwin = oscwin
        self.signal = signal
        self.__bar = None
        self.num = None
        self.__label = None
        self.__graph = None
        self.hidden = False
        oscwin.signal_x_zoom.connect(self.__slot_retick)

    def embed(self, bar: 'SignalBar', num: int):
        self.__bar = bar
        self.num = num
        self.__label = self.__bar.ctrl.sig_add(self)
        self.__label.setText(f"{self.signal.name}\n{self.signal.pnum}/{self.signal.off}")
        self.__graph = self.__bar.gfx.sig_add()
        self.__graph.setData(self.__bar.table.oscwin.x_coords, y_coords(self.signal.pnum, self.signal.off), True)
        self.__graph.setPen(QPen(self.signal.color))

    def detach(self):
        self.__bar.ctrl.sig_del(self.num)
        self.__bar.gfx.sig_del(self.__graph)
        self.num = None
        self.__bar = None

    def set_hidden(self, hide: bool):
        if self.hidden != hide:
            self.__label.setHidden(hide)
            self.__graph.setVisible(not hide)
            self.hidden = hide
            self.__bar.update_stealth()

    def __slot_retick(self):
        """Update scatter style on x-zoom change"""
        if self.__graph:
            now = self.__graph.scatterStyle().shape() != QCPScatterStyle.ssNone
            need = self.__oscwin.x_sample_width_px >= SCATTER_BOUND_PX
            if now != need:
                self.__graph.setScatterStyle(QCPScatterStyle(
                    QCPScatterStyle.ssPlus if need else QCPScatterStyle.ssNone
                ))
                self.__graph.parentPlot().replot()  # bad solution but ...


class SignalBar(QObject):
    table: 'SignalBarTable'
    row: int
    signals: list[SignalSuit]
    zoom_y: int
    ctrl: BarCtrlWidget
    gfx: BarPlotWidget
    signal_zoom_y_changed = pyqtSignal()

    def __init__(self, table: 'SignalBarTable', row: int = -1):
        super().__init__()
        if not (0 <= row < table.rowCount()):
            row = table.rowCount()
        self.table = table
        self.row = row
        self.signals = list()
        self.zoom_y = 1
        self.ctrl = BarCtrlWidget(self)
        self.gfx = BarPlotWidget(self)
        self.table.bars.insert(self.row, self)
        self.table.insertRow(self.row)
        self.table.setCellWidget(self.row, 0, self.ctrl)
        self.table.setCellWidget(self.row, 1, self.gfx)
        self.table.oscwin.signal_unhide_all.connect(self.__slot_unhide_all)

    def suicide(self):
        del self.table.bars[self.row]
        self.table.removeCellWidget(self.row, 0)
        self.table.removeCellWidget(self.row, 1)
        self.table.removeRow(self.row)
        self.ctrl.close()
        self.gfx.close()
        self.deleteLater()

    @property
    def sig_count(self) -> int:
        return len(self.signals)

    def sig_add(self, ss: SignalSuit):
        ss.embed(self, len(self.signals))
        self.signals.append(ss)
        self.update_stealth()

    def sig_move(self, i: int, other_bar: 'SignalBar'):
        ss = self.signals[i]
        del self.signals[i]
        ss.detach()
        other_bar.sig_add(ss)
        if self.signals:
            for i, ss in enumerate(self.signals):
                ss.num = i
            self.update_stealth()
        else:
            self.suicide()

    def update_stealth(self):
        """Update visibility according to children"""
        hide_me = True
        for ss in self.signals:
            hide_me &= ss.hidden
        if hide_me != self.table.isRowHidden(self.row):
            self.table.setRowHidden(self.row, hide_me)

    def __slot_unhide_all(self):
        for ss in self.signals:
            ss.set_hidden(False)
        if self.table.isRowHidden(self.row):
            self.table.setRowHidden(self.row, False)

    def zoom_dy(self, dy: int):
        """Y-zoom button changed"""
        if dy:
            if 1 <= self.zoom_y + dy <= 1000:
                self.zoom_y += dy
                self.signal_zoom_y_changed.emit()
        elif self.zoom_y > 1:
            self.zoom_y = 1
            self.signal_zoom_y_changed.emit()


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
        # selection
        self.setSelectionMode(self.NoSelection)  # specialy for Anchor
        # self.setSelectionMode(self.SingleSelection)  # default
        # self.setSelectionBehavior(self.SelectRows)
        # DnD
        # self.setDragEnabled(True)  # default=False for Anchor
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

    def __drop_on(self, __evt: QDropEvent) -> Tuple[int, bool]:
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

    def __chk_dnd_event(self, src_object, dst_row_num: int, over: bool) -> int:
        """Check whether drop event acceptable.
        :param src_object: Source object
        :param dst_row_num: Destination object row number
        :param over: Source object overlaps (True) or insert before (False) destination object
        :return:
        - 0: n/a
        - 1: bar move
        - 2: signal join/move
        - 3: signal unjoin
        """
        if dst_row_num >= 0:
            if isinstance(src_object, BarCtrlWidget.Anchor):
                if not over:
                    return int(
                        src_object.parent().bar.table != self or
                        (dst_row_num - src_object.parent().bar.row) not in {0, 1}
                    )
            elif isinstance(src_object, BarCtrlWidget.SignalLabelList):
                if over:
                    return 2 * int(src_object.parent().bar.table != self or src_object.parent().bar.row != dst_row_num)
                else:  # sig.Ins
                    return 3 * int(src_object.count() > 1)
        return 0

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime = event.mimeData()
        # print(mime.formats())  # ['application/x-qabstractitemmodeldatalist']
        super().dragEnterEvent(event)  # paint decoration (not works w Anchor)
        event.accept()  # hack (enable Anchor)

    def dragMoveEvent(self, event: QDragMoveEvent):
        super().dragMoveEvent(event)  # paint decoration (not works w Anchor)
        src_object = event.source()
        dst_row_num, over = self.__drop_on(event)  # SignalBarTable/SignalLabelList
        if self.__chk_dnd_event(src_object, dst_row_num, over):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.isAccepted():
            super().dropEvent(event)
            return
        src_object = event.source()
        dst_row_num, over = self.__drop_on(event)  # SignalBarTable/SignalLabelList
        todo = self.__chk_dnd_event(src_object, dst_row_num, over)
        if todo == 1:  # Bar.Ins
            src_object.parent().bar.table.bar_move(src_object.parent().bar.row, self.bar_insert(dst_row_num))
        elif todo == 2:  # Sig.Ovr (join, move)
            src_object.parent().bar.sig_move(src_object.selected_row, self.bars[dst_row_num])
            src_object.clearSelection()
        elif todo == 3:  # Sig.Ins (unjoin)
            src_object.parent().bar.sig_move(src_object.selected_row, self.bar_insert(dst_row_num))
            src_object.clearSelection()
        event.accept()
        event.setDropAction(Qt.IgnoreAction)

    def __slot_resize_col_ctrl(self, x: int):
        self.setColumnWidth(0, x)

    @property
    def selected_row(self) -> int:  # FIXME: not required w/ Anchor
        return self.selectedIndexes()[0].row()

    def bar_insert(self, row: int = -1) -> SignalBar:
        bar = SignalBar(self, row)
        self.setRowHeight(bar.row, BAR_HEIGHT)
        return bar

    def bar_move(self, row: int, other_bar: SignalBar):
        """Move self bar content to other"""
        bar = self.bars[row]
        for i in range(bar.sig_count):
            bar.sig_move(0, other_bar)
        other_bar.gfx.plot.replot()


class XScroller(QScrollBar):
    signal_update_plots = pyqtSignal()

    def __init__(self, parent: 'OscWindow'):
        """
        :param parent:
        :type parent: ComtradeWidget
        :note: An idea:
        - full width = plot width (px)
        - page size = current col1 width (px)
        """
        super().__init__(Qt.Horizontal, parent)
        parent.signal_x_zoom.connect(self.__slot_update_range)
        parent.tb.plot.signal_width_changed.connect(self.__slot_update_page)

    @property
    def norm_min(self) -> float:
        """Normalized (0..1) left page position"""
        return self.value() / (self.maximum() + self.pageStep())

    @property
    def norm_max(self) -> float:
        """Normalized (0..1) right page position"""
        return (self.value() + self.pageStep()) / (self.maximum() + self.pageStep())

    def __slot_update_range(self):
        """Update maximum against new x-zoom.
        (x_width_px changed, page (px) - not)"""
        page = self.pageStep()
        x_width_px = self.parent().x_width_px
        max_new = self.parent().x_width_px - self.pageStep()
        v_new = min(
            max_new,
            max(
                0,
                round((self.value() + page / 2) / (self.maximum() + page) * x_width_px - (page / 2))
            )
        )
        self.setMaximum(max_new)
        if v_new != self.value():
            self.setValue(v_new)  # emit signal
        else:
            self.signal_update_plots.emit()

    def __slot_update_page(self, new_page: int):
        """Update page against new signal windows width"""
        x_max = self.parent().x_width_px
        if min(new_page, self.pageStep()) < x_max:
            if new_page > x_max:
                new_page = x_max
            self.setPageStep(new_page)
            v0 = self.value()
            self.setMaximum(self.parent().x_width_px - new_page)  # WARN: value changed w/o signal emit
            if self.value() == v0:
                self.signal_update_plots.emit()  # Force update plots; plan B: self.valueChanged.emit(self.value())


class OscWindow(QWidget):
    x_zoom: int  # current X_PX_WIDTH_uS index
    x_coords: list[float]
    tb: TopBar
    # cb: QWidget
    lst1: SignalBarTable
    lst2: SignalBarTable
    hs: XScroller
    col_ctrl_width = COL_CTRL_WIDTH_INIT
    act_unhide: QAction
    act_x_zoom_in: QAction
    act_x_zoom_out: QAction
    signal_resize_col_ctrl = pyqtSignal(int)
    signal_unhide_all = pyqtSignal()
    signal_x_zoom = pyqtSignal()

    def __init__(self, data: list[Signal], parent: QMainWindow):
        super().__init__(parent)
        self.x_zoom = len(X_PX_WIDTH_uS) - 1  # initial: max
        # self.x_coords = [SIG_WIDTH * 1000 / SIN_SAMPLES * i - SIG_WIDTH / 500 for i in range(SIN_SAMPLES + 1)]
        self.x_coords = [(SIG_WIDTH * i / SIN_SAMPLES - SIG_WIDTH / 2) * 1000 for i in range(SIN_SAMPLES + 1)]
        self.__mk_widgets()
        self.__mk_layout()
        self.__mk_actions()
        self.__mk_menu(parent)
        self.__set_data(data)
        self.__update_xzoom_actions()
        # special connections
        self.hs.valueChanged.connect(self.tb.plot.slot_rerange_force)
        self.hs.signal_update_plots.connect(self.tb.plot.slot_rerange)

    @property
    def x_width_ms(self) -> float:
        retvalue = self.x_coords[-1] - self.x_coords[0]
        # print("x_width_ms:", retvalue)
        return retvalue

    @property
    def x_width_px(self) -> int:
        retvalue = round(self.x_width_ms * 1000 / X_PX_WIDTH_uS[self.x_zoom])
        # print("x_width_px:", retvalue)
        return retvalue

    @property
    def x_sample_width_px(self) -> int:
        """Current width of samples interval in px"""
        return round(self.x_width_px / SIN_SAMPLES)

    def __mk_widgets(self):
        self.tb = TopBar(self)
        self.lst1 = SignalBarTable(self)
        self.lst2 = SignalBarTable(self)
        self.hs = XScroller(self)

    def __mk_layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tb)
        splitter = QSplitter(Qt.Vertical, self)
        splitter.addWidget(self.lst1)
        splitter.addWidget(self.lst2)
        self.layout().addWidget(splitter)
        self.layout().addWidget(self.hs)
        # decoration
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)

    def __mk_actions(self):
        self.act_unhide = QAction("&Unhide all", self, triggered=self.__do_unhide_all)
        self.act_x_zoom_in = QAction("X-zoom &In", self, shortcut='Ctrl+I', triggered=self.__do_xzoom_in)
        self.act_x_zoom_out = QAction("X-zoom &Out", self, shortcut='Ctrl+O', triggered=self.__do_xzoom_out)

    def __mk_menu(self, parent: QMainWindow):
        menu_view = parent.menuBar().addMenu("&View")
        menu_view.addAction(self.act_unhide)
        menu_view.addAction(self.act_x_zoom_in)
        menu_view.addAction(self.act_x_zoom_out)

    def __set_data(self, data: list[Signal]):
        def __set_data_one(__tbl: SignalBarTable, __data: list[Signal]):
            for __j, __sig in enumerate(__data):
                __tbl.bar_insert(__j).sig_add(SignalSuit(__sig, self))

        n0 = len(data) // 2
        __set_data_one(self.lst1, data[:n0])
        __set_data_one(self.lst2, data[n0:])

    def resize_col_ctrl(self, dx: int):
        if self.col_ctrl_width + dx > COL_CTRL_WIDTH_MIN:
            self.col_ctrl_width += dx
            self.signal_resize_col_ctrl.emit(self.col_ctrl_width)

    def __do_unhide_all(self):
        self.signal_unhide_all.emit()

    def __update_xzoom_actions(self):
        """Set X-zoom actions availability"""
        self.act_x_zoom_in.setEnabled(self.x_zoom > 0)
        self.act_x_zoom_out.setEnabled(self.x_zoom < (len(X_PX_WIDTH_uS) - 1))
        # print("X-zoom:", self.x_zoom)

    def __do_xzoom(self, dxz: int = 0):
        if 0 <= self.x_zoom + dxz < len(X_PX_WIDTH_uS):
            self.x_zoom += dxz
            self.__update_xzoom_actions()
            self.signal_x_zoom.emit()

    def __do_xzoom_in(self):
        self.__do_xzoom(-1)

    def __do_xzoom_out(self):
        self.__do_xzoom(1)


class MainWindow(QMainWindow):
    cw: OscWindow

    def __init__(self):
        super().__init__()
        data = [Signal(
            num=i,
            name=f"sig{i}",
            pnum=random.randint(1, 5),
            off=random.randint(0, SIN_SAMPLES - 1),
            color=COLORS[random.randint(0, len(COLORS) - 1)]
        ) for i in range(BARS)]
        self.cw = OscWindow(data, self)
        self.setCentralWidget(self.cw)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
