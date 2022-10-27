"""огые X-axis."""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow
# 3. 4rd
from QCustomPlot2 import QCustomPlot, QCPAxisRect, QCPAxis
# x. const
X_LIST = tuple(range(-4, 5))  # [-4..4]
Y_LIST = (0, 1, 4, 1, 0, 1, 3, 1, 0)
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))


class MainWindow(QMainWindow):
    def __init__(self, _, parent=None):
        super().__init__(parent)
        # self.setMinimumSize(0, 0)
        cw: QCustomPlot = QCustomPlot(self)
        self.setCentralWidget(cw)
        # lets go
        self.setup_chart(cw)
        self.squeeze(cw.axisRect(0))
        self.color_up(cw)
        cw.replot()

    @staticmethod
    def setup_chart(cw: QCustomPlot):
        # -chart: QCPGraph = cp.addGraph()
        # -chart.setData(X_LIST, Y_LIST)
        cw.xAxis.setRange(X_LIST[0], X_LIST[-1])

    @staticmethod
    def squeeze(ar: QCPAxisRect):
        ar.setMinimumMargins(QMargins())  # the best
        ar.removeAxis(ar.axis(QCPAxis.atTop, 0))
        ar.removeAxis(ar.axis(QCPAxis.atRight, 0))
        ar.removeAxis(ar.axis(QCPAxis.atLeft, 0))
        # clean last axis
        xaxis: QCPAxis = ar.axis(QCPAxis.atBottom, 0)
        # -xaxis.setTickLabels(False)
        # -xaxis.setTicks(False)
        xaxis.setTickLabelSide(QCPAxis.lsInside)
        xaxis.grid().setVisible(False)
        xaxis.setPadding(0)
        xaxis.ticker().setTickCount(len(X_LIST))  # QCPAxisTicker

    @staticmethod
    def color_up(cw: QCustomPlot):
        cw.setBackground(BG_BRUSH)
        cw.axisRect(0).setBackground(FG_BRUSH)

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
