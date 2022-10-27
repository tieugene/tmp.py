"""PySide2 port of the linechart example from Qt v5.x"""
# 1. std
import sys
# 2. 3rd
from PySide2.QtCore import QPointF
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QMainWindow, QApplication
# 3. 4rd
from PySide2.QtCharts import QtCharts


def create_axis(chart, series):
    xaxis = QtCharts.QValueAxis()
    xaxis.setTickType(QtCharts.QValueAxis.TicksDynamic)  # or TicksFixed
    xaxis.setTickAnchor(0)  # dyn
    xaxis.setTickInterval(5)  # dyn
    # xaxis.setTickCount(5)  # fixed ticks; >= 2
    xaxis.setLabelFormat("%d")
    # xaxis.setLabelsVisible(True)
    xaxis.setGridLineVisible(False)
    # xaxis.setLineVisible(True)
    # series.attachAxis(self.xaxis)
    chart.setAxisX(xaxis, series)


class TestChart(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        series = QtCharts.QLineSeries()
        series.append(-12, 0)
        series.append(25, 0)

        chart = QtCharts.QChart()
        chart.legend().hide()
        chart.addSeries(series)
        # self.chart.createDefaultAxes()
        create_axis(chart, series)
        # self.chart.setTitle("Simple line chart example")

        self.chartView = QtCharts.QChartView()
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.chartView.setChart(chart)

        chart.setContentsMargins(0, 0, 0, 0)
        chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chartView.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(self.chartView)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(440, 300)
    sys.exit(app.exec_())
