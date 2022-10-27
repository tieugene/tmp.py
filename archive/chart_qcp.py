"""Linechart with max size.
PyQt5.QCustomPlot version."""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPGraph, QCPAxisRect, QCPAxis
# x. const
X_LIST = tuple(range(-4, 5))  # [-4..4]
Y_LIST = (-1, 0, 3, 0, -1, 0, 2, 0, -1)
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))
ZERO_PEN = QPen(QColor('black'))


class MainWindow(QMainWindow):
    def __init__(self, _, parent=None):
        super().__init__(parent)
        cw: QCustomPlot = QCustomPlot(self)
        self.setCentralWidget(cw)
        # lets go
        self.setup_chart(cw)
        self.squeeze(cw)
        self.color_up(cw)
        cw.replot()

    @staticmethod
    def setup_chart(cw: QCustomPlot):
        chart: QCPGraph = cw.addGraph()
        chart.setData(X_LIST, Y_LIST)
        cw.xAxis.setRange(X_LIST[0], X_LIST[-1])
        cw.yAxis.setRange(min(Y_LIST), max(Y_LIST))

    @staticmethod
    def squeeze(cw: QCustomPlot):
        ar: QCPAxisRect = cw.axisRect(0)
        ar.setMinimumMargins(QMargins())  # the best
        ar.removeAxis(cw.xAxis2)
        ar.removeAxis(cw.yAxis2)
        #cw.yAxis.setVisible(False)  # or cp.graph().valueAxis()
        yaxis = cw.yAxis  # QCPAxis
        yaxis.setTickLabels(False)
        yaxis.setTicks(False)
        # yaxis.grid().setVisible(False)
        # yaxis.grid().setSubGridVisible(False)  # not works
        # yaxis.grid().setPen(QPen(QColor(255, 255, 255, 0)))  # not good but...
        yaxis.grid().setZeroLinePen(ZERO_PEN)
        yaxis.ticker().setTickCount(1)  # the only z-line
        yaxis.setPadding(0)
        xaxis = cw.xAxis  # QCPAxis
        xaxis.setTickLabels(False)
        xaxis.setTicks(False)
        xaxis.grid().setZeroLinePen(ZERO_PEN)
        xaxis.ticker().setTickCount(len(X_LIST))  # QCPAxisTicker
        xaxis.setPadding(0)

    @staticmethod
    def color_up(cw: QCustomPlot):
        cw.setBackground(BG_BRUSH)
        cw.graph(0).setPen(CHART_PEN)
        cw.axisRect(0).setBackground(FG_BRUSH)
        cw.xAxis.setBasePen(QPen(QColor('black')))
        cw.yAxis.setBasePen(QPen(QColor('black')))

    def print_resume(self):
        print(self.centralWidget().size())


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(sys.argv)
    window.show()
    window.resize(400, 200)
    window.print_resume()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
