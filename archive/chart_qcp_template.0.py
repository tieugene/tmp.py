"""PyQt5.QCustomPlot chart template."""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPAxisRect
# x. const
X_LIST = tuple(range(-4, 5))  # [-4..4]
Y_LIST = (-1, 0, 3, 0, -1, 0, 2, 0, -1)
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))
ZERO_PEN = QPen(QColor('black'))


class MyChart(QCustomPlot):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.addGraph().setData(X_LIST, Y_LIST)
        self.xAxis.setRange(X_LIST[0], X_LIST[-1])
        self.yAxis.setRange(min(Y_LIST), max(Y_LIST))
        self.squeeze()
        self.color_up()

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
        xaxis.ticker().setTickCount(len(X_LIST))  # QCPAxisTicker
        xaxis.setPadding(0)

    def color_up(self):
        self.setBackground(BG_BRUSH)
        self.graph().setPen(CHART_PEN)
        self.axisRect(0).setBackground(FG_BRUSH)
        self.xAxis.setBasePen(QPen(QColor('black')))
        self.yAxis.setBasePen(QPen(QColor('black')))


class MainWindow(QMainWindow):
    cw: QCustomPlot

    def __init__(self):
        super().__init__()
        self.__set_widgets()
        self.setCentralWidget(self.cw)
        # self.cw.replot()

    def __set_widgets(self):
        self.cw = MyChart(self)

    def print_resume(self):
        print(self.centralWidget().size())


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 200)
    # window.print_resume()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
