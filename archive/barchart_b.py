#!/usr/bin/env python3
"""Barchart test. Plan B: QListWidget powered
Aim: whether box layout can be stretchable bar chart.
"""
# 1. std
import sys
from typing import Optional
# 2. 3rd
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QScrollArea, QHBoxLayout, QVBoxLayout, QFrame, \
    QListWidget, QTableWidgetItem, QListWidgetItem

# x. const
FONT_STD = QFont('mono', 8)
WIDTH_HRM_TITLE = 75
WIDTH_HRM_LEGEND = 35
HRM_VAL = (100, 50, 25, 12, 6, 3, 1, 0)


def color2style(c: QColor) -> str:
    """Convert QColor into stylesheet-compatible string"""
    return "rgb(%d, %d, %d)" % (c.red(), c.green(), c.blue())


class _SlickHWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)


class _SlickVWidget(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(QMargins())
        self.layout().setSpacing(0)


class _HrmText(_SlickHWidget):
    subj: QLabel

    def __init__(self, parent: 'SignalHarmBar'):
        super().__init__(parent)
        self.subj = QLabel(self)
        self.subj.setFont(FONT_STD)
        self.layout().addWidget(self.subj)


class HrmTitle(_HrmText):
    def __init__(self, no: int, parent: 'SignalHarmBar'):
        super().__init__(parent)
        self.subj.setText(f"{no}: {no * 50} Гц")
        self.setFixedWidth(WIDTH_HRM_TITLE)


class HrmLegend(_HrmText):
    def __init__(self, val: int, parent: 'SignalHarmBar'):
        super().__init__(parent)
        self.subj.setText(f" {val}%")
        self.setFixedWidth(WIDTH_HRM_LEGEND)


class HrmSpace(QFrame):
    def __init__(self, parent: 'SignalHarmBar', color: Optional[QColor] = None):  # TODO: color: bool
        super().__init__(parent)
        if color:
            self.setStyleSheet("background-color: %s" % color2style(color))


class SignalHarmBar(_SlickHWidget):
    title: HrmTitle
    indic: HrmSpace
    legend: HrmLegend
    pad: HrmSpace
    """One harmonic row"""
    def __init__(self, no: int, val: int, color: QColor, parent: 'SignalBar'):
        """
        :param no: Harmonic order number (1..5)
        :param val: Harmonic value, % (0..100)
        :param parent: Subj
        """
        super().__init__(parent)
        # self.setStyleSheet("border: 1px dotted black")
        # 1. mk widgets
        # - title
        self.title = HrmTitle(no, self)
        self.layout().addWidget(self.title)
        self.layout().setStretchFactor(self.title, 0)
        # - indicator
        self.indic = HrmSpace(self, color)
        self.layout().addWidget(self.indic)
        self.layout().setStretchFactor(self.indic, val)
        # - perventage
        self.legend = HrmLegend(val, self)
        self.layout().addWidget(self.legend)
        self.layout().setStretchFactor(self.legend, 0)
        # - pad
        self.indic = HrmSpace(self)
        self.layout().addWidget(self.indic)  # TODO: if pad > 0; ? spacer?
        self.layout().setStretchFactor(self.indic, 100 - val)


class SignalTitleBar(QWidget):
    subj: QLabel

    def __init__(self, text: str, color: QColor, parent: 'SignalBar'):
        super().__init__(parent)
        self.subj = QLabel(text, self)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.subj)
        self.layout().addStretch(0)
        self.setStyleSheet("background-color: %s" % color2style(color))


class SignalBar(QWidget):
    """One signal's things.
    TODO: color up
    """
    def __init__(self, name: str, color: QColor, parent: 'MainWidget'):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(SignalTitleBar(name, color, self))
        for i, v in enumerate(HRM_VAL):
            self.layout().addWidget(SignalHarmBar(i + 1, v, color, self))


class ChartWidget(QWidget):
    def __init__(self, parent: 'QMainWindow'):
        super().__init__(parent)
        # self.setStyleSheet("border: 1px solid red")
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(SignalBar("IA", QColor(Qt.green), self))
        # repeat for each signal
        self.layout().addStretch(0)


class MainWidget(QListWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        item1 = QListWidgetItem("a", self)
        self.setItemWidget(item1, SignalBar("IA", QColor(Qt.green), self))
        item2 = QListWidgetItem("b", self)
        self.setItemWidget(item2, SignalBar("IB", QColor(Qt.yellow), self))


def main() -> int:
    app = QApplication(sys.argv)
    mw = QMainWindow()
    mw.setCentralWidget(MainWidget(mw))
    mw.show()
    # window.resize(400, 300)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
