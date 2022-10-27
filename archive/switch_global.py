#!/usr/bin/env python3
"""Demo of switching class-wide variables"""


class MySignal(object):
    __shifted: bool = False
    __name: str

    def __init__(self, name: str):
        super().__init__()
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def shifted(self):
        return MySignal.__shifted

    @staticmethod
    def shift(v: bool):
        MySignal.__shifted = v


a = MySignal('aaa')
b = MySignal('bbb')
print(a.name, a.shifted)
print(b.name, b.shifted)
b.shift(True)
print(a.name, a.shifted)
print(b.name, b.shifted)
