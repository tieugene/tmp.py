"""gfx_ppreview/data: data source"""
# 1. std
from typing import Tuple, List, Iterator
from dataclasses import dataclass
import math
# 2. 3rd
from PyQt5.QtCore import Qt

# 3. local
# x. consts
AUTOFILL = True
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


@dataclass
class SigSuit:
    is_bool: bool
    name: str
    color: Qt.GlobalColor
    value: list[float]


SigSuitList: List[SigSuit] = list()


def __data_fill():
    """Fill data with predefined or auto"""
    def __gen_predef() -> Iterator[Tuple[str, int, Qt.GlobalColor, bool]]:  # generator of predefined data
        for __d in DATA_PREDEF:
            yield __d

    def __gen_random() -> Iterator[Tuple[str, int, Qt.GlobalColor, bool]]:
        import random
        random.seed()
        for __i in range(SIGNALS):
            yield (
                f"Signal {__i}",
                random.randint(0, SAMPLES - 1),
                _COLORS[random.randint(0, len(_COLORS) - 1)],
                bool(random.randint(0, 1))
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
            is_bool=d[3],
            name=d[0],
            color=d[2],
            value=__mk_sin(d[1]) if d[3] else __mk_meander(d[1])
        ))


if not SigSuitList:
    __data_fill()
