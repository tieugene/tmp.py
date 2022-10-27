"""V-scaling xN.
- H-size: fixed
- H-scroll: is, works (simle)
- V-size: adaptive + zoom x N (reFixedSize, bad idea)
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QIcon, QResizeEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QAction, QScrollArea, QToolBar
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


class MyChart(QCustomPlot):
    src: Data
    __zoom: int

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.__zoom = 1
        self.src = DataSin()
        self.addGraph().setData(self.src.x_list, self.src.y_list)
        self.xAxis.setRange(self.src.x_min, self.src.x_max)
        self.yAxis.setRange(self.src.y_min, self.src.y_max)
        self.__squeeze()
        self.__color_up()
        self.setFixedWidth(400)

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

    @property
    def zoom(self):
        return self.__zoom

    @zoom.setter
    def zoom(self, z: int):
        if z != self.zoom:
            self.__zoom = z
            self.slot_vresize()

    def slot_vresize(self):
        h_vscroller = self.parent().height()
        if self.height() != (new_height := h_vscroller * self.__zoom):
            self.setFixedHeight(new_height)


class MyScrollArea(QScrollArea):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def resizeEvent(self, event: QResizeEvent):
        event.accept()
        if (h_new := event.size().height()) != (h_old := event.oldSize().height()):
            # print("H_old:", h_old)  # can be -1
            # print("H_new:", h_new)
            self.widget().slot_vresize()


class MainWindow(QMainWindow):
    cw: QWidget
    sa: MyScrollArea
    qcp: QCustomPlot
    act_exit: QAction
    act_zoom_in: QAction
    act_zoom_out: QAction
    act_zoom_0: QAction

    def __init__(self):
        super().__init__()
        self.__set_widgets()
        self.setCentralWidget(self.cw)
        self.__set_layout()
        self.__set_actions()
        self.__set_menubar()
        self.__set_toolbar()
        self.__set_connections()

    def __set_widgets(self):
        self.cw = QWidget(self)
        self.sa = MyScrollArea(self.cw)
        self.qcp = MyChart(self.sa)
        self.sa.setWidget(self.qcp)

    def __set_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sa)
        # self.qcp.setFixedHeight(168)  # set to scrollarea real width

    def __set_actions(self):
        self.act_exit = QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                               statusTip="Exit the application", triggered=self.close)
        self.act_zoom_in = QAction(QIcon.fromTheme("zoom-in"), "V-Zoom &in", self, shortcut="Ctrl++",
                               statusTip="Vertical zoom in", triggered=self.__do_zoom_in)
        self.act_zoom_out = QAction(QIcon.fromTheme("zoom-out"), "V-Zoom &out", self, shortcut="Ctrl+-",
                               statusTip="Vertical zoom out", triggered=self.__do_zoom_out)
        self.act_zoom_0 = QAction(QIcon.fromTheme("zoom-original"), "V-Zoom &0", self, shortcut="Ctrl+0",
                               statusTip="Vertical zoom reset", triggered=self.__do_zoom_0)

    def __set_menubar(self):
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_exit)
        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(self.act_zoom_in)
        menu_view.addAction(self.act_zoom_out)
        menu_view.addAction(self.act_zoom_0)

    def __set_toolbar(self):
        tb = QToolBar(self)
        self.addToolBar(tb)
        tb.addAction(self.act_zoom_in)
        tb.addAction(self.act_zoom_0)
        tb.addAction(self.act_zoom_out)

    def __set_connections(self):
        ...

    def __do_zoom_in(self):
        self.qcp.zoom += 1

    def __do_zoom_out(self):
        if self.qcp.zoom > 1:
            self.qcp.zoom -= 1

    def __do_zoom_0(self):
        self.qcp.zoom = 1


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(300, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
