"""gfx_ppreview/consts: constants"""
# 1. std
# 2. 3rd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
# x. consts
# - user defined
DEBUG = False  # paint borders around some items
PORTRAIT = False  # initial orientation
# -- ...
# - hardcoded
W_PAGE = (1130, 748)  # Page width landscape/portrait; (A4-10mm)/0.254mm
W_LABEL = 53  # Label column width
H_HEADER = 56  # Header height, like 4×14
H_ROW_BASE = 28  # Base (slick) row height in landscape mode; like 2×14
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
Hotkeys: ^0: Original size, ^O: Switch landscape/portrait, ^V: Close (hide),
Go page: ^↑: 1st, ^←: Prev., ^→: Next, ^↓: Last.
'''