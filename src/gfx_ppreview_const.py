"""gfx_ppreview constants"""
# 1. std
from typing import Tuple
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
# x. consts
# - user defined
DEBUG = False  # paint borders around some items
PORTRAIT = True  # initial orientation
AUTOFILL = False
# -- ...
SAMPLES = 24  # samples per signal
SIGNALS = 10  # Number of signals for autofill
# - hardcoded
W_PAGE = (1130, 748)  # Page width landscape/portrait; (A4-10mm)/0.254mm
W_LABEL = 53  # Label column width
H_HEADER = 56
H_ROW_BASE = 28  # Base (slick) row height in landscape mode
H_BOTTOM = 20  # Bottom scale height
PPP = 6  # plots per page
FONT_MAIN = QFont('mono', 8)  # 7×14
COLORS = (
    Qt.GlobalColor.black,
    Qt.GlobalColor.red,
    Qt.GlobalColor.darkRed,
    Qt.GlobalColor.green,
    Qt.GlobalColor.darkGreen,
    Qt.GlobalColor.blue,
    Qt.GlobalColor.darkBlue,
    Qt.GlobalColor.cyan,
    Qt.GlobalColor.darkCyan,
    Qt.GlobalColor.magenta,
    Qt.GlobalColor.darkMagenta,
    Qt.GlobalColor.yellow,
    Qt.GlobalColor.darkYellow,
    Qt.GlobalColor.gray,
    Qt.GlobalColor.darkGray,
    Qt.GlobalColor.lightGray
)
# y. data
HEADER_TXT = '''This is the header with 3 lines.
Hotkeys: ^0: original size, ^P portrait, ^L: landscape, ^V: close,
Pageing: ^↑: 1st page, ^←: Prev. page, ^→: Next page, ^↓: Last page.
'''
TICS = {  # scale tics {sample_no: text}
    0: 123,
    5: 456,
    SAMPLES * 0.98: 789
}
# name, x-offset/perios, color, analog
DataValue = Tuple[str, int, Qt.GlobalColor, bool]
DATA_PREDEF = (
    ("Signal 1", 0, Qt.GlobalColor.black, True),
    ("Signal 22", 1, Qt.GlobalColor.red, True),
    ("Signal 333", 2, Qt.GlobalColor.blue, True),
    ("Signal 4444", 3, Qt.GlobalColor.green, False),
    ("Signal 5", 4, Qt.GlobalColor.magenta, False),
    ("Signal 6", 5, Qt.GlobalColor.darkYellow, True),
    ("Signal 10", 6, Qt.GlobalColor.cyan, True),
    ("Signal 11", 7, Qt.GlobalColor.darkGreen, True),
    ("Signal 12", 8, Qt.GlobalColor.yellow, True),
    ("Signal 13", 9, Qt.GlobalColor.darkBlue, True),
)
DATA = []
