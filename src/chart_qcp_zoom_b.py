"""Zoom/scroll.A - QCP axis reRange:
- V-size adaptive + zoom x N
- H-size: zoom x N
- H-scroller: ok
:note: predecessor: chart_qcp_vsroll.py
:todo: scale/zoom > scroller | qcp
:todo: ptrs recalc (e.g. on zoom)
:todo: grid
:todo: x_zoom 1..2..5 x 10ⁿ == 10..5..2..1 // 2
:todo: simplify, optimize
"""
# 1. std
import sys
import math
# 2. 3rd
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QAction, QScrollBar, QToolBar, QHBoxLayout
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPAxisRect
# x. const
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))
ZERO_PEN = QPen(QColor('black'))
BK_PEN = QPen(QColor('black'))
SIN_X_STEP = 15
SIN_Y_MAX = 10
SIN_Y_OFFSET = 0
# CHART_WIDTH_0 = 400
X_PPU_0 = 20  # X-axis px per unit


class DataSin(object):
    _x_list: list[int]
    _y_list: list[float] = []

    def __init__(self, period_split_by: int = 24, width: int = 24, x_min: int = -12):
        """
        :param period_split_by: Parts divide period to
        :param width: Period size, X units
        :param x_min: X-offset, X units
        :todo: periods: float | rational
        """
        x_step: int = width // period_split_by
        self._x_list = list(range(x_min, width + x_min + x_step, x_step))
        x_step_deg = 360 // period_split_by
        for i, x in enumerate(range(0, 360 + x_step_deg, x_step_deg)):
            self._x_list.append(i * x_step)
            self._y_list.append(math.sin(math.radians(x)) * SIN_Y_MAX + SIN_Y_OFFSET)

    @property
    def count(self) -> int:
        return len(self._y_list)

    @property
    def x_list(self) -> list:
        return self._x_list

    @property
    def x_min(self) -> int:
        return self._x_list[0]

    @property
    def x_max(self) -> int:
        return self._x_list[-1]

    @property
    def width(self) -> int:
        return self.x_max - self.x_min

    @property
    def y_list(self) -> list:
        return self._y_list

    @property
    def y_min(self) -> float:
        return min(self._y_list)

    @property
    def y_max(self) -> float:
        return max(self._y_list)

    @property
    def height(self) -> float:
        return self.y_max - self.y_min


class Chart(QCustomPlot):
    """
    Teach:
    - QCPAxis.scaleRange() (multiply once)
    - ~~QCPAxis.setScaleRatio()~~  # against other axis; usual for ms/mus
    """
    __src: DataSin
    __zoom_y: int
    __zoom_x: int
    __y_scroller: QScrollBar
    __x_scroller: QScrollBar

    def __init__(self, y_scroller: QScrollBar, x_scroller: QScrollBar, parent: QWidget):
        super().__init__(parent)
        self.__y_scroller = y_scroller
        self.__x_scroller = x_scroller
        self.__zoom_y = 1
        self.__zoom_x = 1
        self.__src = DataSin()
        self.addGraph().setData(self.__src.x_list, self.__src.y_list)
        self.__squeeze()
        self.__color_up()
        self.yAxis.setRange(self.__src.y_min, self.__src.y_max)
        self.xAxis.setRange(self.__src.x_min, self.__src.x_max)
        self.__y_scroller.valueChanged.connect(self.__slot_move_y)
        self.__x_scroller.slot_chart_resize(self.vpxwidth)
        self.__x_scroller.valueChanged.connect(self.__slot_move_x)

    def __squeeze(self):
        ar: QCPAxisRect = self.axisRect(0)
        ar.setMinimumMargins(QMargins())  # the best
        ar.removeAxis(self.xAxis2)
        ar.removeAxis(self.yAxis2)
        # cw.yAxis.setVisible(False)  # or cp.graph().valueAxis()
        yaxis = self.yAxis  # QCPAxis
        yaxis.setTickLabels(False)
        yaxis.setTicks(False)
        # yaxis.grid().setVisible(False)
        # yaxis.grid().setSubGridVisible(False)  # not works
        # yaxis.grid().setPen(QPen(QColor(255, 255, 255, 0)))  # not good but...
        yaxis.grid().setZeroLinePen(ZERO_PEN)
        yaxis.ticker().setTickCount(1)  # the only z-line
        yaxis.setPadding(0)
        xaxis = self.xAxis  # QCPAxis
        xaxis.setTickLabels(False)
        xaxis.setTicks(False)
        xaxis.grid().setZeroLinePen(ZERO_PEN)
        xaxis.ticker().setTickCount(self.__src.count)  # QCPAxisTicker
        xaxis.setPadding(0)

    def __color_up(self):
        self.setBackground(BG_BRUSH)
        self.graph().setPen(CHART_PEN)
        self.axisRect(0).setBackground(FG_BRUSH)
        self.xAxis.setBasePen(BK_PEN)
        self.yAxis.setBasePen(BK_PEN)

    @property
    def vpxwidth(self) -> int:
        """Virtual width in px"""
        return self.__src.width * self.__zoom_x * X_PPU_0

    def slot_zoom_y(self, z: int):
        # FIXME: sync w/ Y-scroller
        if self.__zoom_y == z:
            return
        self.yAxis.scaleRange(self.__zoom_y/z)
        self.__zoom_y = z
        self.replot()

    def __slot_move_y(self, y: int):
        """Calc __move as old_range_start and new
        :fixme: simplify
        :fixme: now 'native scrolling'
        """
        scroller_ptr = y / (self.__y_scroller.maximum() + self.__y_scroller.pageStep())
        self_ptr = (self.yAxis.range().lower - self.__src.y_min) / self.__src.height
        d_ptr = (scroller_ptr - self_ptr) * self.__src.height
        self.yAxis.moveRange(d_ptr)
        self.replot()

    def slot_zoom_x(self, z: int):
        if self.__zoom_x == z:
            return
        self.xAxis.scaleRange(self.__zoom_x/z)  # FIXME: expand tails
        self.__zoom_x = z
        self.__x_scroller.slot_chart_resize(self.vpxwidth)
        # self.replot()

    def __slot_move_x(self, x: int):
        """Move self range according to global X-scroller.
        :param x: Current X-scroller position as px in zoom x CHART_WIDTH_0 range
        :todo: simplify
        """
        scroller_ptr = x / (self.__x_scroller.maximum() + self.__x_scroller.pageStep())
        ptr_l = self.__src.x_min + scroller_ptr * self.__src.width
        d_ptr = self.__src.width * self.width() / self.vpxwidth
        self.xAxis.setRange(ptr_l, ptr_l + d_ptr)
        self.replot()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if (width_new := event.size().width()) != (width_old := event.oldSize().width()):
            self.__x_scroller.slot_chart_rewidth(width_old, width_new)


class YScroller(QScrollBar):
    __zoom: int

    def __init__(self, parent: QWidget):
        super().__init__(Qt.Vertical, parent)
        self.__zoom = 1

    @property
    def zoom(self) -> int:
        return self.__zoom

    def __recalc(self):
        page = self.height()
        size = page * self.__zoom  # full scroller range
        max_range = size - page
        self.setPageStep(page)
        self.setRange(0, max_range)
        # FIXME: tune yscroller.value()
        if self.value() > max_range:
            self.setValue(max_range)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if (height_old := event.oldSize().height()) == (height_new := event.size().height()):
            return
        self.__recalc()
        # FIXME: recalc ptr

    def slot_zoom(self, z: int):
        if self.__zoom == z:
            return
        self.__zoom = z
        self.__recalc()
        self.setValue(round(self.maximum() / 2))  # FIXME: now strictly centered


class ChartArea(QWidget):
    qcp: Chart
    vsb: YScroller

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.__set_widgets()
        self.__set_layout()
        # parent.signal_zoom_y.connect(self.qcp.slot_zoom_y)
        parent.signal_zoom_y.connect(self.vsb.slot_zoom)
        parent.signal_zoom_x.connect(self.qcp.slot_zoom_x)

    def __set_widgets(self):
        self.vsb = YScroller(self)
        self.qcp = Chart(self.vsb, self.parent().xsb, self)

    def __set_layout(self):
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.qcp)
        self.layout().addWidget(self.vsb)


class XScroller(QScrollBar):
    __zoom: int
    __size: int  # full scroller range == range + page

    def __init__(self, parent: QWidget):
        super().__init__(Qt.Horizontal, parent)
        self.__zoom = 1
        self.__size = 0
        self.setPageStep(0)

    def __recalc(self):
        if self.__size and (page := self.pageStep()):
            if page > self.__size:
                self.setPageStep(page := self.__size)
            max_range = self.__size - page  # FIXME: or -1?
            self.setRange(0, max_range)
            # FIXME: tune yscroller.value()
            if self.value() > max_range:
                self.setValue(max_range)
            else:
                self.valueChanged.emit(self.value())

    def __slot_zoom(self, z: int):
        if self.__zoom == z:
            return
        self.__zoom = z
        self.__recalc()
        self.setValue(round(self.maximum() / 2))  # FIXME: now strictly centered

    def slot_chart_resize(self, size: int):
        self.__size = size
        self.__recalc()

    def slot_chart_rewidth(self, w_old: int, w_new: int):
        self.setPageStep(w_new)
        self.__recalc()


class MainWindow(QMainWindow):
    __zoom_x: int
    __zoom_y: int
    cw: QWidget
    csa: ChartArea
    xsb: XScroller
    act_exit: QAction
    act_yzoom_in: QAction
    act_yzoom_out: QAction
    act_yzoom_0: QAction
    act_xzoom_in: QAction
    act_xzoom_out: QAction
    act_xzoom_0: QAction
    signal_zoom_y = pyqtSignal(int)
    signal_zoom_x = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.__zoom_x = 1
        self.__zoom_y = 1
        self.__set_widgets()
        self.setCentralWidget(self.cw)
        self.__set_layout()
        self.__set_actions()
        self.__set_menubar()
        self.__set_toolbar()
        self.__set_connections()

    def __set_widgets(self):
        self.cw = QWidget(self)
        self.xsb = XScroller(self)
        self.csa = ChartArea(self)  # warning: after xsb

    def __set_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.csa)
        layout.addWidget(self.xsb)
        self.cw.setLayout(layout)

    def __set_actions(self):
        self.act_exit = QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                triggered=self.close)
        self.act_yzoom_in = QAction(QIcon.fromTheme("zoom-in"), "V-Zoom in", self, shortcut="Ctrl+Up",
                                    triggered=self.__do_yzoom_in)
        self.act_yzoom_out = QAction(QIcon.fromTheme("zoom-out"), "V-Zoom out", self, shortcut="Ctrl+Down",
                                     triggered=self.__do_yzoom_out)
        self.act_yzoom_0 = QAction(QIcon.fromTheme("zoom-original"), "V-Zoom 0", self, shortcut="Ctrl+0",
                                   triggered=self.__do_yzoom_1)
        self.act_xzoom_in = QAction(QIcon(), "H-Zoom in", self, shortcut="Ctrl+Right",
                                    triggered=self.__do_xzoom_in)
        self.act_xzoom_out = QAction(QIcon(), "H-Zoom out", self, shortcut="Ctrl+Left",
                                     triggered=self.__do_xzoom_out)
        self.act_xzoom_0 = QAction(QIcon(), "H-Zoom 0", self, shortcut="Ctrl+Equal",
                                   triggered=self.__do_xzoom_0)
        self.act_xzoom_in.setIconText("↔")
        self.act_xzoom_in.setToolTip("H-Zoom In")
        self.act_xzoom_out.setIconText("><")
        self.act_xzoom_out.setToolTip("H-Zoom Out")
        self.act_xzoom_0.setIconText('||')
        self.act_xzoom_0.setToolTip("H-Zoom reset")

    def __set_menubar(self):
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_exit)
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(self.act_yzoom_in)
        menu_view.addAction(self.act_yzoom_out)
        menu_view.addAction(self.act_yzoom_0)
        menu_view.addAction(self.act_xzoom_in)
        menu_view.addAction(self.act_xzoom_out)
        menu_view.addAction(self.act_xzoom_0)

    def __set_toolbar(self):
        tb = QToolBar(self)
        self.addToolBar(tb)
        tb.addAction(self.act_yzoom_out)
        tb.addAction(self.act_yzoom_0)
        tb.addAction(self.act_yzoom_in)
        tb.addAction(self.act_xzoom_out)
        tb.addAction(self.act_xzoom_0)
        tb.addAction(self.act_xzoom_in)

    def __set_connections(self):
        ...

    def __do_yzoom_in(self):
        self.__zoom_y += 1
        self.signal_zoom_y.emit(self.__zoom_y)

    def __do_yzoom_out(self):
        if self.__zoom_y == 1:
            return
        self.__zoom_y -= 1
        self.signal_zoom_y.emit(self.__zoom_y)

    def __do_yzoom_1(self):
        if self.__zoom_y == 1:
            return
        self.__zoom_y = 1
        self.signal_zoom_y.emit(self.__zoom_y)

    def __do_xzoom_in(self):
        self.__zoom_x += 1
        self.signal_zoom_x.emit(self.__zoom_x)

    def __do_xzoom_out(self):
        if self.__zoom_x == 1:
            return
        self.__zoom_x -= 1
        self.signal_zoom_x.emit(self.__zoom_x)

    def __do_xzoom_0(self):
        if self.__zoom_x == 1:
            return
        self.__zoom_x = 1
        self.signal_zoom_x.emit(self.__zoom_x)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(300, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
