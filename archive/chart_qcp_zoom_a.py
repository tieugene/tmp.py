"""Zoom/scroll.A - reFixedSize QCP:
- V-size adaptive + zoom x N (reFixedSize)
- H-size: zoom x N (reFixed)
- H-scroller: ok
:note: predecessor: chart_qcp_vscale.py
:todo: hide qca in csa (signal/slot)
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QAction, QScrollArea, QScrollBar, QToolBar
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPAxisRect
# 4. local
from graph_source import Data, DataSimple, DataSin
# x. const
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))
ZERO_PEN = QPen(QColor('black'))
BK_PEN = QPen(QColor('black'))
CHART_WIDTH_0 = 400


class ChartArea(QScrollArea):
    signal_height_changed = pyqtSignal(int, int)
    signal_width_changed = pyqtSignal(int, int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event: QResizeEvent):
        event.accept()
        if (height_new := event.size().height()) != (height_old := event.oldSize().height()):
            self.signal_height_changed.emit(height_old, height_new)
        if (width_new := event.size().width()) != (widht_old := event.oldSize().width()):
            self.signal_width_changed.emit(widht_old, width_new)


class Chart(QCustomPlot):
    src: Data
    __y_zoom: int

    def __init__(self, parent: ChartArea):
        super().__init__(parent)
        self.__y_zoom = 1
        self.__x_zoom = 1
        self.src = DataSin()
        self.addGraph().setData(self.src.x_list, self.src.y_list)
        self.xAxis.setRange(self.src.x_min, self.src.x_max)
        self.yAxis.setRange(self.src.y_min, self.src.y_max)
        self.__squeeze()
        self.__color_up()
        parent.signal_height_changed.connect(self.slot_chg_height)

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
        xaxis.ticker().setTickCount(self.src.count)  # QCPAxisTicker
        xaxis.setPadding(0)

    def __color_up(self):
        self.setBackground(BG_BRUSH)
        self.graph().setPen(CHART_PEN)
        self.axisRect(0).setBackground(FG_BRUSH)
        self.xAxis.setBasePen(BK_PEN)
        self.yAxis.setBasePen(BK_PEN)

    def __set_height(self, h: int):
        self.setFixedHeight(h)

    @property
    def yzoom(self):
        return self.__y_zoom

    @yzoom.setter
    def yzoom(self, z: int):
        if z != self.__y_zoom:
            self.__y_zoom = z
            self.__set_height(self.parent().height() * self.__y_zoom)

    def slot_chg_height(self, _: int, h_new: int):
        # vscroller_height = self.parent().height()
        if self.height() != (new_height := h_new * self.__y_zoom):  # for direct signal/slot
            self.__set_height(new_height)

    def slot_chg_width(self, w: int):
        self.setFixedWidth(w)


class XScroller(QScrollBar):
    __chart_width: int

    def __init__(self, parent: QWidget):
        super().__init__(Qt.Horizontal, parent)
        self.__chart_width = 0

    @property
    def __sibling(self) -> QScrollBar:
        return self.parent().parent().csa.horizontalScrollBar()

    def slot_csa_width_changed(self, _: int, w_new: int):
        """Recalc parms on QSA width changed"""
        self.setPageStep(w_new)
        self.__sibling.setPageStep(w_new)
        max_new = max(0, self.__chart_width - self.pageStep())
        self.setRange(0, max_new)
        self.__sibling.setRange(0, max_new)
        if self.value() > max_new:
            self.setValue(max_new)

    def slot_chart_width_changed(self, w_new: int):
        """Recalc scroller parm on aim column resized with mouse.
        :param w_new: New chart column width
        """
        self.__chart_width = w_new
        # defaults: pageStep == 10, range == 0..99
        max_new = max(0, self.__chart_width - self.pageStep())
        self.setRange(0, max_new)
        self.__sibling.setRange(0, max_new)


class MainWindow(QMainWindow):
    __zoom_x: int
    cw: QWidget
    csa: ChartArea
    qcp: Chart
    xsb: XScroller
    act_exit: QAction
    act_yzoom_in: QAction
    act_yzoom_out: QAction
    act_yzoom_0: QAction
    act_xzoom_in: QAction
    act_xzoom_out: QAction
    act_xzoom_0: QAction
    signal_set_char_width = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.__zoom_x = 1
        self.__set_widgets()
        self.setCentralWidget(self.cw)
        self.__set_layout()
        self.__set_actions()
        self.__set_menubar()
        self.__set_toolbar()
        self.__set_connections()
        self.__set_chart_width()

    def __set_widgets(self):
        self.cw = QWidget(self)
        self.csa = ChartArea(self)
        self.qcp = Chart(self.csa)
        self.csa.setWidget(self.qcp)
        self.xsb = XScroller(self)

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
                                   triggered=self.__do_yzoom_0)
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
        self.signal_set_char_width.connect(self.qcp.slot_chg_width)
        self.xsb.valueChanged.connect(self.csa.horizontalScrollBar().setValue)
        # self.csa.horizontalScrollBar().rangeChanged.connect(self.xsb.setRange)
        # self.csa.horizontalScrollBar().pageStepChanged => xsb.setPageStep()
        self.csa.signal_width_changed.connect(self.xsb.slot_csa_width_changed)
        self.signal_set_char_width.connect(self.xsb.slot_chart_width_changed)

    def __set_chart_width(self):
        self.signal_set_char_width.emit(CHART_WIDTH_0 * self.__zoom_x)

    def __do_yzoom_in(self):
        self.qcp.yzoom += 1

    def __do_yzoom_out(self):
        if self.qcp.yzoom > 1:
            self.qcp.yzoom -= 1

    def __do_yzoom_0(self):
        if self.qcp.yzoom != 1:
            self.qcp.yzoom = 1

    def __do_xzoom_in(self):
        self.__zoom_x += 1
        self.__set_chart_width()

    def __do_xzoom_out(self):
        if self.__zoom_x > 1:
            self.__zoom_x -= 1
            self.__set_chart_width()

    def __do_xzoom_0(self):
        if self.__zoom_x != 1:
            self.__zoom_x = 1
            self.__set_chart_width()


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(300, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
