"""PyQt5.QCustomPlot chart template."""
# 1. std
import sys
# 2. 3rd
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QBrush, QColor, QPen, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar
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

    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.src = DataSin()
        self.addGraph().setData(self.src.x_list, self.src.y_list)
        self.xAxis.setRange(self.src.x_min, self.src.x_max)
        self.yAxis.setRange(self.src.y_min, self.src.y_max)
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
        xaxis.ticker().setTickCount(self.src.count)  # QCPAxisTicker
        xaxis.setPadding(0)

    def color_up(self):
        self.setBackground(BG_BRUSH)
        self.graph().setPen(CHART_PEN)
        self.axisRect(0).setBackground(FG_BRUSH)
        self.xAxis.setBasePen(BK_PEN)
        self.yAxis.setBasePen(BK_PEN)


class MainWindow(QMainWindow):
    cw: QCustomPlot
    act_exit: QAction

    def __init__(self):
        super().__init__()
        self.__set_widgets()
        self.setCentralWidget(self.cw)
        # self.__set_actions()
        # self.__set_menubar()
        # self.__set_toolbar()
        # self.cw.replot()

    def __set_widgets(self):
        self.cw = MyChart(self)

    def __set_actions(self):
        self.act_exit = QAction(QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q",
                                statusTip="Exit the application", triggered=self.close)

    def __set_menubar(self):
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction(self.act_exit)

    def __set_toolbar(self):
        tb = QToolBar(self)
        self.addToolBar(tb)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(400, 200)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
