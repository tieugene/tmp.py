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
SAMPLES = 12  # samples per signal
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
# is_bool, name, color, h-offset/h-offset [0..SAMPLES], v-offset(%)/half-period[1+]
_DataSource = Tuple[bool, str, Qt.GlobalColor, int, int]
DATA_PREDEF = (
    (False, "Sig 1", Qt.GlobalColor.black, 0, 0),
    (True, "Sign 2 b", Qt.GlobalColor.red, 1, 1),
    (False, "Sig 3 aa", Qt.GlobalColor.blue, 2, 50),
    (True, "Sign 4 bbb", Qt.GlobalColor.green, 0, 2),
    (False, "Sig 5 aaaa", Qt.GlobalColor.magenta, 4, -50),
    (True, "Sig 6 bbbbb", Qt.GlobalColor.darkYellow, 2, 2),
    (False, "Sig 8 (a)", Qt.GlobalColor.cyan, 6, 90),
    (True, "Sig 9 (b)", Qt.GlobalColor.darkGreen, 7, -90),
    (False, "Sig 11", Qt.GlobalColor.darkMagenta, 8, 0),
    (False, "Sig 12", Qt.GlobalColor.darkBlue, 9, 0),
)


@dataclass
class SigSuit:  # TODO: => ASigSuit + BSigSuit
    is_bool: bool
    name: str
    color: Qt.GlobalColor
    value: list[float]


SigSuitList: List[SigSuit] = list()


def __data_fill():
    """Fill data with predefined or auto"""
    def __gen_predef() -> Iterator[_DataSource]:  # generator of predefined data
        for __d in DATA_PREDEF:
            yield __d

    def __gen_random() -> Iterator[_DataSource]:
        import random
        random.seed()
        for __i in range(SIGNALS):
            __is_bool = bool(random.randint(0, 1))
            yield (
                __is_bool,
                f"Signal {__i}",
                _COLORS[random.randint(0, len(_COLORS) - 1)],
                random.randint(0, SAMPLES - 1),
                random.randint(0, 9) if __is_bool else random.randint(-90, 90),
            )

    def __mk_sin(ho: int, vo: int) -> List[float]:
        """
        Make sinusoide graph coordinates. Y=0..1
        :param ho: H-Offset, points
        :param vo: V-Offset, %x10
        :return: list of y (0..1)
        """
        return [(math.sin((i + ho) * 2 * math.pi / SAMPLES)) + vo / 100 for i in range(SAMPLES + 1)]

    def __mk_meander(ho: int, hp: int) -> List[float]:
        """Make meander. Starts from 0.
        :param ho: H-Offset, tics
        :param hp: Half-Period, tics
        """
        hp = hp % SAMPLES or 1  # Deviding by 0 protection
        return [int((i+ho) / hp) % 2 for i in range(SAMPLES + 1)]

    for d in __gen_random() if AUTOFILL else __gen_predef():
        SigSuitList.append(SigSuit(
            is_bool=d[0],
            name=d[1],
            color=d[2],
            value=__mk_meander(d[3], d[4]) if d[0] else __mk_sin(d[3], d[4])
        ))


if not SigSuitList:
    __data_fill()
