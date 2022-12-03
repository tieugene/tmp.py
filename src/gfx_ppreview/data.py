"""gfx_ppreview/data: data source"""
# 1. std
from typing import Tuple
# 2. 3rd
from PyQt5.QtCore import Qt
# x. consts
AUTOFILL = True
SAMPLES = 24  # samples per signal
SIGNALS = 50  # Number of signals for autofill
TICS = {  # scale tics {sample_no: text}
    0: 123,
    5: 456,
    SAMPLES * 0.98: 789
}
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
