"""gfx_ppreview constants"""
# 1. std
from typing import Tuple
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DEBUG = False
W_PAGE = (1130, 748)  # Page width landscape/portrait; (A4-10mm)/0.254mm
W_LABEL = 53  # Label column width
H_HEADER = 56
H_ROW_BASE = 28  # Base (slick) row height in landscape mode
H_BOTTOM = 20  # Bottom scale height
SAMPLES = 12
PPP = 5  # plots per page
FONT_MAIN = QFont('mono', 8)  # 7×14
HEADER_TXT = '''This is the header with 3[4] lines.
Use "Ctrl+0" to original size, "Ctr-P" to portrait, "Ctr+L" to landscape (default), "Ctrl+V" to close.
Last line.
'''
DataValue = Tuple[str, int, Qt.GlobalColor, bool]
DATA = (  # name, x-offset, color, wide
    ("Signal 1", 0, Qt.GlobalColor.black, True),
    ("Signal 22", 1, Qt.GlobalColor.red, True),
    ("Signal 333", 2, Qt.GlobalColor.blue, False),
    ("Signal 4444", 3, Qt.GlobalColor.green, True),
    ("Signal 5", 4, Qt.GlobalColor.magenta, True),
    ("Signal 6", 5, Qt.GlobalColor.yellow, True),
)
TICS = {  # scale tics
    0: 123,
    5: 456,
    SAMPLES * 0.98: 789
}
