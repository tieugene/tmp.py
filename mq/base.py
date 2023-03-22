"""Base for mq engines."""
from typing import Dict, Type
from abc import ABC, abstractmethod


class MQE(RuntimeError):
    """Basic error."""

    def __str__(self):
        """Make string representation of exception."""
        if uplink := super().__str__():
            return f"{self.__class__.__name__}: {uplink}"
        return self.__class__.__name__


class MQ(ABC):
    """Queue itself (one object per queue)."""
    _master: 'MQCollection'
    _id: int

    @abstractmethod
    def count(self) -> int:
        """Get messages count."""
        ...

    @abstractmethod
    def put(self, data: bytes):
        """Put message."""
        ...

    @abstractmethod
    def get(self, wait: bool = True) -> bytes:
        """Get a message."""
        ...

    def __init__(self, master: 'MQCollection', _id: int):
        self._master = master
        self._id = _id


class MQCollection:
    """Container to uniq MQs."""
    _child_cls: Type[MQ]
    _store: Dict[int, MQ] = {}
    _count: int

    def __init__(self, cls: Type[MQ]):
        self._child_cls = cls
        self._store = {}
        self._count = 0

    def init(self, count: int):
        self._count = count

    def q(self, i: int) -> MQ:
        if i >= self._count:
            raise MQE(f"Too big num {i}")
        if i not in self._store:
            self._store[i] = self._child_cls(self, i)
        return self._store[i]
