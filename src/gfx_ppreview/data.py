"""gfx_ppreview/data: data source"""
# 1. std
from typing import Tuple, List, Iterator
from dataclasses import dataclass
import math
# 2. 3rd
from PyQt5.QtCore import Qt
# 3. local
# x. consts
AUTOFILL = False
SAMPLES = 24  # samples per signal
SIGNALS = 50  # Number of signals for autofill
_COLORS = (
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
TICS = {  # scale tics {sample_no: text}
    0: 123,
    5: 456,
    SAMPLES * 0.98: 789
}
DATA_PREDEF = (  # name, offset/period, color, is_bool
    (False, "Signal 1", Qt.GlobalColor.black, 0),
    (True, "Signal 22", Qt.GlobalColor.red, 1),
    (False, "Signal 333", Qt.GlobalColor.blue, 2),
    (True, "Signal 4444", Qt.GlobalColor.green, 3),
    (True, "Signal 5", Qt.GlobalColor.magenta, 4),
    (False, "Signal 6", Qt.GlobalColor.darkYellow, 5),
    (False, "Signal 10", Qt.GlobalColor.cyan, 6),
    (False, "Signal 11", Qt.GlobalColor.darkGreen, 7),
    (False, "Signal 12", Qt.GlobalColor.yellow, 8),
    (False, "Signal 13", Qt.GlobalColor.darkBlue, 9),
)


@dataclass
class SigSuit:
    is_bool: bool
    name: str
    color: Qt.GlobalColor
    value: list[float]


SigSuitList: List[SigSuit] = list()


def __data_fill():
    """Fill data with predefined or auto"""
    def __gen_predef() -> Iterator[Tuple[bool, str, Qt.GlobalColor, int]]:  # generator of predefined data
        for __d in DATA_PREDEF:
            yield __d

    def __gen_random() -> Iterator[Tuple[bool, str, Qt.GlobalColor, int]]:
        import random
        random.seed()
        for __i in range(SIGNALS):
            yield (
                bool(random.randint(0, 1)),
                f"Signal {__i}",
                _COLORS[random.randint(0, len(_COLORS) - 1)],
                random.randint(0, SAMPLES - 1),
            )

    def __mk_sin(o: int = 0) -> List[float]:  # FIXME: hide
        """
        Make sinusoide graph coordinates. Y=0..1
        :param o: Offset, points
        :return: list of y (0..1)
        """
        return [(1 + math.sin((i + o) * 2 * math.pi / SAMPLES)) / 2 for i in range(SAMPLES + 1)]

    def __mk_meander(p: int) -> List[float]:  # FIXME: hide
        """Make meander. Starts from 0.
        :param p: Period
        """
        p = p % SAMPLES or 1
        return [int(i / p) % 2 for i in range(SAMPLES + 1)]

    for d in __gen_random() if AUTOFILL else __gen_predef():
        SigSuitList.append(SigSuit(
            is_bool=d[0],
            name=d[1],
            color=d[2],
            value=__mk_meander(d[3]) if d[0] else __mk_sin(d[3])
        ))


if not SigSuitList:
    __data_fill()
