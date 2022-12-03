"""gfx_ppreview/data: data source"""
# 1. std
from typing import Tuple, List
import math
# 2. 3rd
from PyQt5.QtCore import Qt

from src.gfx_ppreview.consts import COLORS

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


def mk_sin(o: int = 0) -> List[float]:
    """
    Make sinusoide graph coordinates. Y=0..1
    :param o: Offset, points
    :return: list of y (0..1)
    """
    return [(1 + math.sin((i + o) * 2 * math.pi / SAMPLES)) / 2 for i in range(SAMPLES + 1)]


def mk_meander(p: int) -> List[float]:
    """Make meander. Starts from 0.
    :param p: Period
    """
    p = p % SAMPLES or 1
    return [int(i / p) % 2 for i in range(SAMPLES + 1)]


def data_fill():
    """Fill data witth predefined or auto"""
    if AUTOFILL:
        import random
        random.seed()
        for i in range(SIGNALS):
            DATA.append((
                f"Signal {i}",
                random.randint(0, SAMPLES-1),
                COLORS[random.randint(0, len(COLORS)-1)],
                bool(random.randint(0, 1))
            ))
    else:
        DATA.extend(DATA_PREDEF)
