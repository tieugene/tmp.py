"""Main pointer sample.
Changelog:
- 0: as is (curve)
- 1: QCPItemStraightLine, X-only ptr; vline not required; cleaned up
TODO:
- on mouse: signal/slot
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPAxisRect, QCPAxis, QCPGraph, QCPItemTracer, QCPItemLine, QCPItemStraightLine

# x. const
X_LIST = tuple(range(-4, 5))  # [-4..4]
Y_LIST = (0, 1, 4, 1, 0, 1, 3, 1, 0)
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))
PTR_PEN = QPen(QBrush(QColor('orange')), 2)
VLINE_PEN = QPen(QBrush(QColor('green')), 1, Qt.DotLine)


class MainPtr(QCPItemTracer):
    def __init__(self, cp: QCustomPlot):
        super().__init__(cp)
        self.setGraph(cp.graph())
        self.setPen(PTR_PEN)
        self.position.setAxes(cp.xAxis, None)


class VLine(QCPItemStraightLine):
    def __init__(self, cp: QCustomPlot):
        super().__init__(cp)
        self.setPen(VLINE_PEN)
        self.setVisible(False)

    def move2x(self, x: float):
        """
        :param x:
        :note: for  QCPItemLine: s/point1/start/, s/point2/end/
        """
        # self.point1.setCoords(x, self.parentPlot().yAxis.range().lower)  # FIXME: bad for const line
        # self.point2.setCoords(x, self.parentPlot().yAxis.range().upper)
        self.point1.setCoords(x, 0)
        self.point2.setCoords(x, 1)


class MainWindow(QMainWindow):
    label: QLabel
    cp: QCustomPlot
    ptr: MainPtr
    vline: VLine
    to_paint: bool

    def __init__(self):
        super().__init__()
        self.to_paint = False
        cw: QWidget = QWidget(self)
        self.setCentralWidget(cw)
        layout: QVBoxLayout = QVBoxLayout(cw)
        self.label = QLabel(cw)
        self.cp = QCustomPlot(cw)
        layout.addWidget(self.label)
        layout.addWidget(self.cp)
        # lets go
        self.setup_chart(self.cp)
        self.squeeze(self.cp)
        self.ptr = MainPtr(self.cp)
        self.vline = VLine(self.cp)
        # self.color_up(self.cp)
        self.cp.mousePress.connect(self.__slot_mouse_press)
        self.cp.mouseMove.connect(self.__slot_mouse_move)
        self.cp.mouseRelease.connect(self.__slot_mouse_release)
        # self.cp.replot()

    @staticmethod
    def setup_chart(cw: QCustomPlot):
        chart: QCPGraph = cw.addGraph()
        chart.setData(X_LIST, Y_LIST)
        cw.xAxis.setRange(X_LIST[0], X_LIST[-1])
        # print(cw.yAxis.range())

    @staticmethod
    def squeeze(cp: QCustomPlot):
        cp.yAxis.setVisible(False)
        ar: QCPAxisRect = cp.axisRect(0)
        ar.removeAxis(cp.xAxis2)
        ar.removeAxis(cp.yAxis2)
        ar.setMinimumMargins(QMargins())  # the best
        xaxis: QCPAxis = cp.xAxis
        # xaxis.setTickLabels(False)
        # xaxis.setTicks(False)
        xaxis.setPadding(0)

    @staticmethod
    def color_up(cp: QCustomPlot):
        cp.setBackground(BG_BRUSH)
        cp.graph(0).setPen(CHART_PEN)
        cp.axisRect(0).setBackground(FG_BRUSH)

    def __switch_trace(self, todo: bool):
        # print(("Off", "On")[int(todo)])
        self.to_paint = todo
        self.vline.setVisible(todo)

    def __handle_mouse(self, x_px: int):
        """
        Handle mouse pressed[+moved]
        :param x_px: mouse x-position (px)
        """
        x_src = self.cp.xAxis.pixelToCoord(x_px)  # real x-position realtive to graph z-point
        self.ptr.setGraphKey(x_src)
        pos = self.ptr.position  # coerced x-postion
        self.vline.move2x(x_src)
        self.label.setText(f"x: {pos.key()}, y: {pos.value()}")
        self.cp.replot()

    def __slot_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.__switch_trace(True)
            self.__handle_mouse(event.x())

    def __slot_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.__switch_trace(False)
            self.cp.replot()

    def __slot_mouse_move(self, event: QMouseEvent):
        if self.to_paint:  # or `event.buttons() & Qt.LeftButton`
            self.__handle_mouse(event.x())


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
