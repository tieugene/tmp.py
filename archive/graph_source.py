# Data source for graphs
import math

SIN_X_STEP = 15
SIN_Y_MAX = 10
SIN_Y_OFFSET = 0


class Data(object):
    __slots__ = ()
    _x_min: int = 0
    _y_list: list = []

    @property
    def count(self) -> int:
        return len(self._y_list)

    @property
    def width(self) -> int:
        return self.count

    @property
    def x_min(self) -> int:
        return self._x_min

    @property
    def x_max(self) -> int:
        return self._x_min + self.count - 1  # FIXME:

    @property
    def x_list(self) -> list:
        return list(range(self._x_min, self._x_min + self.count))

    @property
    def y_min(self) -> int:
        return min(self._y_list)

    @property
    def y_max(self) -> int:
        return max(self._y_list)

    @property
    def y_list(self) -> list:
        return self._y_list

    @property
    def height(self) -> int:
        return self.y_max - self.y_min + 1


class DataSimple(Data):
    _x_min: int = -4
    _y_list: list = [-1, 0, 3, 0, -1, 0, 2, 0, -1]


class DataSin(Data):
    def __init__(self, step: int = SIN_X_STEP):
        """

        :param step: Angles to divide 360° to
        :todo: width of period, units, int (default 1 xu / step)
        :todo: step => pieces
        """
        super().__init__()
        self._x_min = -360 // step // 2
        for x in range(0, 360 + step, step):
            self._y_list.append(math.sin(math.radians(x)) * SIN_Y_MAX + SIN_Y_OFFSET)
