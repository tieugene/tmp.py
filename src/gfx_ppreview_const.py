from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DEBUG = True
W_PAGE = (1130, 748)  # Page width landscape/portrait; (A4-10mm)/0.254mm
W_LABEL = 53  # width of label column
H_BOTTOM = 20  # Height of bottom scale
# W_GRAPH_STEP = W_LABEL // 4
# H_GRAPH = 14  # bigger makes label b-cutted
POINTS = 12
PPP = 5  # plots per page
FONT_MAIN = QFont('mono', 8)  # 7×14
DataValue = Tuple[str, int, Qt.GlobalColor]
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line.\n"
DATA = (  # name, x-offset, color
    ("Signal 1", 0, Qt.GlobalColor.black),
    ("Signal 22", 1, Qt.GlobalColor.red),
    ("Signal 333", 2, Qt.GlobalColor.blue),
    ("Signal 4444", 3, Qt.GlobalColor.green),
    ("Signal 5", 4, Qt.GlobalColor.yellow),
    ("Signal 6", 5, Qt.GlobalColor.magenta),
)
