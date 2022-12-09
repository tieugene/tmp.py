"""gfx_ppreview/data: data source"""
# 1. std
from typing import Tuple, List, Iterator, Union, Dict, Optional
from dataclasses import dataclass
import math
# 2. 3rd
from PyQt5.QtCore import Qt
# 3. local
from utils import gc2str

# 3. local
# x. consts
SAMPLES = 24  # samples per signal
__AUTOFILL = False
__SIGNALS = 50  # Number of signals for autofill
__AUTOBARS = 50  # Number of signal bars
__SPB = 3  # max signal per bar
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
_SigSource = Tuple[bool, str, Qt.GlobalColor, int, int]
_BarSource = Dict[str, Union[int, List[_SigSource]]]
DATA_PREDEF = (
    {'d': [(False, "Sig 0.0", Qt.GlobalColor.black, 0, 0)]},
    {'d': [(True, "Sign 1.0 b", Qt.GlobalColor.red, 1, 1)]},  # 1, 1
    {'d': [(False, "Sig 2.0 a", Qt.GlobalColor.cyan, 0, 0),
     (False, "Sig 2.1 a", Qt.GlobalColor.blue, 4, 50)]},
    {'d': [(True, "Sign 4 bbb", Qt.GlobalColor.green, 0, 2),
     (False, "Sig 5 aaaa", Qt.GlobalColor.magenta, 4, -50)]},
    {'d': [(True, "Sig 6 bbbbb", Qt.GlobalColor.darkYellow, 2, 2)]},
    {'d': [(False, "Sig 8 (a)", Qt.GlobalColor.cyan, 6, 90)]},
    {'d': [(True, "Sig 9 (b)", Qt.GlobalColor.darkGreen, 7, 0)], 'h': 75},
    {'d': [(False, "Sig 11", Qt.GlobalColor.darkMagenta, 8, -200)], 'h': 175},
    {'d': [(False, "Sig 12", Qt.GlobalColor.darkBlue, 9, 0)]},
)
# DATA_PREDEF = ([(False, "Sig 0.0", Qt.GlobalColor.black, 0, 0)],)  # 1-line version


@dataclass
class _SigSuitBase:
    """
    :note: Adjusted values: max >= 0, min <= 0
    :note: n* members are for 'normalized' adjusted values (nmax - nmin = 1 const)
    """
    name: str
    color: Qt.GlobalColor
    value: Union[List[int], List[float]]
    # amin: Union[int, float]  # Adjusted absulute min value (min but ≤ 0)
    # amax: Union[int, float]  # Adjusted absulute max value (max but ≥ 0)
    # anmin: Union[int, float]  # Adjusted normalized [nominal] min (-1..0)
    # anmax: Union[int, float]  # Adjusted normalized [nominal] max (0..1)
    # nvalue: Union[List[int], List[float]]  # (adjusted) Normalized values (amax-amin=1)

    @property
    def count(self) -> int:
        return len(self.value)


@dataclass
class ASigSuit(_SigSuitBase):  # TODO: calc helping vars in __init__
    value: List[float]
    is_bool: bool = False

    @property
    def amin(self) -> float:
        return min(0, min(self.value))

    @property
    def amax(self) -> float:
        return max(0, max(self.value))

    @property
    def __asize(self) -> float:
        return self.amax - self.amin

    @property
    def anmin(self) -> float:
        return self.amin/self.__asize

    @property
    def anmax(self) -> float:
        return self.amax/self.__asize

    @property
    def nvalue(self) -> List[float]:
        return [v / self.__asize for v in self.value]


@dataclass
class BSigSuit(_SigSuitBase):
    value: List[int]
    is_bool: bool = True
    amin: int = 0
    amax: int = 1
    anmin: int = 0
    anmax: int = 1

    @property
    def nvalue(self) -> List[int]:
        return self.value


USigSuitType = Union[ASigSuit, BSigSuit]


class BarSuit(List[USigSuitType]):
    h: Optional[int]

    @property
    def is_bool(self) -> bool:
        """Check if is pure B"""
        for ss in self:
            if not ss.is_bool:
                return False
        return True

    @property
    def html(self) -> str:
        # FIXME: ''.join([...])
        lbl = ''
        for ss in self:
            lbl += f"<span style='color: {gc2str(ss.color)}'>{ss.name}</span><br/>"
        return lbl


BarSuitList = List[BarSuit]
barsuit_list: BarSuitList = list()


def __data_fill():
    """Fill data with predefined or auto"""

    def __gen_predef() -> Iterator[_BarSource]:  # generator of predefined data
        for __d in DATA_PREDEF:
            yield __d

    def __gen_random() -> Iterator[_BarSource]:
        import random
        random.seed()
        for __bn in range(__AUTOBARS):
            __data = list()
            for __sn in range(random.randint(1, __SPB)):
                __is_bool = bool(random.randint(0, 1))
                __data.append((
                    __is_bool,
                    f"Sig {__bn}.{__sn}",
                    _COLORS[random.randint(0, len(_COLORS) - 1)],
                    random.randint(0, SAMPLES - 1),
                    random.randint(0, 9) if __is_bool else random.randint(-90, 90),
                ))
            __bar = {'d': __data}
            if random.randint(0, 1):
                __bar['h'] = random.randint(50, 300)
            yield __bar

    def __mk_sin(ho: int, vo: int) -> List[float]:
        """
        Make sinusoide graph coordinates. Y=0..1
        :param ho: H-Offset, points
        :param vo: V-Offset, %x10
        :return: list of y (0..1)
        """
        return [round((math.sin((i + ho) * 2 * math.pi / SAMPLES)) + vo / 100, 3) for i in range(SAMPLES + 1)]

    def __mk_meander(ho: int, hp: int) -> List[int]:
        """Make meander. Starts from 0.
        :param ho: H-Offset, tics
        :param hp: Half-Period, tics
        """
        hp = hp % SAMPLES or 1  # Deviding by 0 protection
        return [int((i + ho) / hp) % 2 for i in range(SAMPLES + 1)]

    for bd in __gen_random() if __AUTOFILL else __gen_predef():
        is_bool = True
        data = bd['d']
        bs = BarSuit()
        for d in data:
            if d[0]:
                ss = BSigSuit(
                    name=d[1],
                    color=d[2],
                    value=__mk_meander(d[3], d[4])
                )
            else:
                ss = ASigSuit(
                    name=d[1],
                    color=d[2],
                    value=__mk_sin(d[3], d[4])
                )
            is_bool &= d[0]
            bs.append(ss)
        bs.h = None if is_bool else bd.get('h')
        barsuit_list.append(bs)


if not barsuit_list:
    __data_fill()
