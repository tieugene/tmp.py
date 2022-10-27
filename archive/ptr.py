"""Main pointer sample.
Changelog:
- 0: as is (curve)
- 1: QCPItemStraightLine, X-only ptr; vline not required; cleaned up
- 2: signal/slot
"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPAxisRect, QCPItemTracer, QCPItemStraightLine

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
        """
        self.point1.setCoords(x, 0)
        self.point2.setCoords(x, 1)


class MyQCP(QCustomPlot):
    ptr: MainPtr
    vline: VLine
    to_paint: bool

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.to_paint = False
        self.setup_chart()
        self.squeeze()
        self.ptr = MainPtr(self)
        self.vline = VLine(self)
        self.mousePress.connect(self.__slot_mouse_press)
        self.mouseRelease.connect(self.__slot_mouse_release)
        self.mouseMove.connect(self.__slot_mouse_move)

    def setup_chart(self):
        self.addGraph()
        self.graph().setData(X_LIST, Y_LIST)
        self.xAxis.setRange(X_LIST[0], X_LIST[-1])
        # print(cw.yAxis.range())

    def squeeze(self):
        self.yAxis.setVisible(False)
        ar: QCPAxisRect = self.axisRect(0)
        ar.removeAxis(self.xAxis2)
        ar.removeAxis(self.yAxis2)
        ar.setMinimumMargins(QMargins())  # the best
        # self.xAxis.setTickLabels(False)
        # self.xAxis.setTicks(False)
        self.xAxis.setPadding(0)

    def color_up(self):
        self.setBackground(BG_BRUSH)
        self.graph().setPen(CHART_PEN)
        self.axisRect(0).setBackground(FG_BRUSH)

    def __handle_mouse(self, x_px: int):
        """
        Handle mouse pressed[+moved]
        :param x_px: mouse screen x-position (px)
        """
        x_src = self.xAxis.pixelToCoord(x_px)  # real x-position realtive to graph z-point
        self.ptr.setGraphKey(x_src)
        pos = self.ptr.position  # coerced x-postion
        self.vline.move2x(x_src)
        # self.label.setText(f"x: {pos.key()}, y: {pos.value()}")
        self.replot()
        # TODO: signal to MW: "ptr_moved(pos)"

    def __switch_trace(self, todo: bool):
        # print(("Off", "On")[int(todo)])
        self.to_paint = todo
        self.vline.setVisible(todo)

    def __slot_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.__switch_trace(True)
            self.__handle_mouse(event.x())

    def __slot_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.__switch_trace(False)
            self.replot()

    def __slot_mouse_move(self, event: QMouseEvent):
        """:todo: chk x changed"""
        if self.to_paint:  # or `event.buttons() & Qt.LeftButton`
            self.__handle_mouse(event.x())


class MainWindow(QMainWindow):
    label: QLabel
    cp: MyQCP

    def __init__(self):
        super().__init__()
        cw: QWidget = QWidget(self)
        self.setCentralWidget(cw)
        layout: QVBoxLayout = QVBoxLayout(cw)
        self.label = QLabel(cw)
        self.cp = MyQCP(cw)
        layout.addWidget(self.label)
        layout.addWidget(self.cp)
        # lets go
        # self.cp.replot()

    def __handle_mouse(self, x_px: int):
        """
        Handle mouse pressed[+moved]
        :param x_px: mouse x-position (px)
        """
        x_src = self.cp.xAxis.pixelToCoord(x_px)  # real x-position realtive to graph z-point
        self.ptr.setGraphKey(x_src)
        pos = self.ptr.position  # coerced x-postion
        self.label.setText(f"x: {pos.key()}, y: {pos.value()}")
        # self.cp.replot()
        # TODO: emit signal MainPtrMove(x)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
