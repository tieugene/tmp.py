"""V-scroll QCP via ext. V-scroller and vice versa.
Based on [tutorial](https://www.qcustomplot.com/index.php/tutorials/specialcases/scrollbar)
"""
# 1. std
import sys
import math
# 2. 3rd
from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QSizePolicy, QScrollBar, QAction
# 3. 4rd
from QCustomPlot2 import QCP, QCustomPlot, QCPAxisRect, QCPRange
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

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.src = DataSimple()
        self.addGraph().setData(self.src.x_list, self.src.y_list)
        self.xAxis.setRange(self.src.x_min, self.src.x_max)
        self.yAxis.setRange(self.src.y_min, self.src.y_max)
        self.squeeze()
        self.color_up()
        self.axisRect().setupFullAxesBox(True)  # ???
        self.setInteractions(QCP.Interactions(QCP.iRangeDrag | QCP.iRangeZoom))

    def squeeze(self):
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

    def color_up(self):
        self.setBackground(BG_BRUSH)
        self.graph().setPen(CHART_PEN)
        self.axisRect(0).setBackground(FG_BRUSH)
        self.xAxis.setBasePen(BK_PEN)
        self.yAxis.setBasePen(BK_PEN)


class MainWindow(QMainWindow):
    cw: QWidget
    qcp: QCustomPlot
    vsb: QScrollBar
    act_exit: QAction

    def __init__(self):
        super().__init__()
        self.__set_widgets()
        self.setCentralWidget(self.cw)
        self.__set_layout()
        # setup scroller
        self.vsb.setRange(-500, 500)
        self.qcp.yAxis.setRange(0, 2, Qt.AlignCenter)
        self.vsb.valueChanged.connect(self.__slot_vsb_changed)
        self.qcp.yAxis.rangeChanged.connect(self.__slot_yaxis_changed)

    def __set_widgets(self):
        self.cw = QWidget(self)
        self.qcp = MyChart(self.cw)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.qcp.sizePolicy().hasHeightForWidth())
        self.qcp.setSizePolicy(size_policy)
        self.vsb = QScrollBar(self.cw)
        self.vsb.setOrientation(Qt.Vertical)

    def __set_layout(self):
        grid_layout = QGridLayout(self.cw)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)
        grid_layout.addWidget(self.qcp, 0, 0, 1, 1)
        grid_layout.addWidget(self.vsb, 0, 1, 1, 1)

    def __slot_vsb_changed(self, v: int):
        """Move Y-axis range on V-scroller moved.
        :param v: New slider value, -500..500 (top..bottom)
        :note: dont replot twice if user is dragging plot
        """
        if math.fabs(self.qcp.yAxis.range().center() + v / 100.0) > 0.01:
            self.qcp.yAxis.setRange(-v / 100.0, self.qcp.yAxis.range().size(), Qt.AlignCenter)
            self.qcp.replot()

    def __slot_yaxis_changed(self, r: QCPRange):
        """Move V-scroller on graph moved/zoomed.
        :param r: Range
        """
        # print(r)
        self.vsb.setValue(round(-r.center()*100.0))  # adjust position of scroll bar slider
        self.vsb.setPageStep(round(r.size()*100.0))  # adjust size of scroll bar slider


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
