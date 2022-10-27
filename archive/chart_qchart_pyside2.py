"""Linechart with max size.
PySide2.QChart version."""
# 1. std
import sys
# 2. 3rd
from PySide2.QtCore import QMargins
from PySide2.QtGui import QPainter, QBrush, QColor, QFont, QPen
from PySide2.QtWidgets import QApplication, QMainWindow
# 3. 4rd
from PySide2.QtCharts import QtCharts
# x. const
X_LIST = tuple(range(-4, 5))  # [-4..4]
Y_LIST = (0, 1, 4, 1, 0, 1, 3, 1, 0)
NOFONT = QFont('', 1)
BG_BRUSH = QBrush(QColor('blue'))
FG_BRUSH = QBrush(QColor('yellow'))
CHART_PEN = QPen(QColor('red'))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        cw: QtCharts.QChartView = QtCharts.QChartView()
        self.setCentralWidget(cw)
        # lets go
        self.setup_chart(cw)
        self.squeeze(cw.chart())
        self.color_up(cw.chart())
        cw.setRenderHint(QPainter.Antialiasing)

    @staticmethod
    def setup_chart(cw: QtCharts.QChartView):
        def mk_xaxis() -> QtCharts.QValueAxis:
            xaxis = QtCharts.QValueAxis()
            xaxis.setTickType(QtCharts.QValueAxis.TicksDynamic)
            xaxis.setTickAnchor(0)
            xaxis.setTickInterval(1)
            xaxis.setGridLineVisible(True)
            xaxis.setLabelsFont(NOFONT)
            xaxis.setLabelsVisible(False)
            xaxis.setLineVisible(False)
            xaxis.setTitleFont(NOFONT)
            xaxis.setTitleVisible(False)
            # xaxis.setVisible(False)
            return xaxis

        series: QtCharts.QLineSeries = QtCharts.QLineSeries()
        for i, x in enumerate(X_LIST):
            series.append(x, Y_LIST[i])
        chart: QtCharts.QChart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setAxisX(mk_xaxis(), series)
        cw.setChart(chart)

    @staticmethod
    def squeeze(chart: QtCharts.QChart):
        chart.legend().hide()
        chart.setMargins(QMargins())  # default=20
        # chart.setContentsMargins(-35, -20, -35, -45)  # hack
        chart.layout().setContentsMargins(0, 0, 0, 0)  # default=6

    @staticmethod
    def color_up(chart: QtCharts.QChart):
        chart.series()[0].setPen(CHART_PEN)
        chart.setBackgroundVisible(True)
        chart.setBackgroundBrush(BG_BRUSH)
        chart.setPlotAreaBackgroundVisible(True)
        chart.setPlotAreaBackgroundBrush(FG_BRUSH)

    def print_resume(self):
        print(self.centralWidget().size())
        print(self.centralWidget().chart().plotArea())


def main() -> int:
    app = QApplication()
    window = MainWindow()
    window.show()
    window.resize(400, 200)
    window.print_resume()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
