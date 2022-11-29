from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DEBUG = True
W_PAGE = (1130, 748)  # Page width landscape/portrait; (A4-10mm)/0.254mm
W_LABEL = 53  # Label column width
H_ROW_BASE = 28  # Base (slick) row height in landscape mode
H_BOTTOM = 20  # Bottom scale height
# W_GRAPH_STEP = W_LABEL // 4
# H_GRAPH = 14  # bigger makes label b-cutted
POINTS = 12
PPP = 5  # plots per page
FONT_MAIN = QFont('mono', 8)  # 7×14
HEADER_TXT = "This is the header.\nWith 3 lines.\nLast line.\n"
DataValue = Tuple[str, int, Qt.GlobalColor, bool]
DATA = (  # name, x-offset, color, wide
    ("Signal 1", 0, Qt.GlobalColor.black, True),
    ("Signal 22", 1, Qt.GlobalColor.red, True),
    ("Signal 333", 2, Qt.GlobalColor.blue, False),
    ("Signal 4444", 3, Qt.GlobalColor.green, False),
    ("Signal 5", 4, Qt.GlobalColor.magenta, True),
    ("Signal 6", 5, Qt.GlobalColor.yellow, False),
)
