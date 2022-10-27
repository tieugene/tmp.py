"""X-axis.
PyQt5.QtChart version"""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow
# 3. 4rd
from PyQt5 import QtChart
# x. const
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))


class MainWindow(QMainWindow):
    def __init__(self, _, parent=None):
        super().__init__(parent)
        cw = QtChart.QChartView()
        self.setCentralWidget(cw)
        # lets go
        self.setup_chart(cw)
        self.squeeze(cw.chart())
        self.color_up(cw.chart())
        cw.setRenderHint(QPainter.Antialiasing)

    @staticmethod
    def setup_chart(cw: QtChart.QChartView):
        def mk_axis():
            xaxis = QtChart.QValueAxis()
            xaxis.setTickType(QtChart.QValueAxis.TicksDynamic)  # or TicksFixed
            xaxis.setTickAnchor(0)  # dyn
            xaxis.setTickInterval(5)  # dyn
            xaxis.setLabelsFont(QFont('mono', 8))
            xaxis.setLabelFormat("%d")
            xaxis.setGridLineVisible(False)
            # xaxis.setLineVisible(False)
            xaxis.setTitleFont(NOFONT)
            xaxis.setTitleVisible(False)
            return xaxis

        series = QtChart.QLineSeries()
        series.append(-12, 0)
        series.append(25, 0)
        chart = QtChart.QChart()
        chart.addSeries(series)
        chart.setAxisX(mk_axis(), series)
        cw.setChart(chart)

    @staticmethod
    def squeeze(chart: QtChart.QChart):
        chart.legend().hide()
        chart.setMargins(QMargins())  # default=20
        chart.setContentsMargins(0, 0, 0, 0)
        # chart.setContentsMargins(-35, -20, -35, -45)  # hack
        chart.layout().setContentsMargins(0, 0, 0, 0)  # default=6

    @staticmethod
    def color_up(chart: QtChart.QChart):
        chart.setBackgroundVisible(True)
        chart.setBackgroundBrush(BG_BRUSH)
        chart.setPlotAreaBackgroundVisible(True)
        chart.setPlotAreaBackgroundBrush(FG_BRUSH)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(sys.argv)
    window.resize(400, 200)
    window.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
