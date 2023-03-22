"""Base for mq engines."""
from typing import Dict, Type
from abc import ABC, abstractmethod


class MQE(RuntimeError):
    """Message Queue Exception."""

    def __str__(self):
        """Make string representation of exception."""
        if uplink := super().__str__():
            return f"{self.__class__.__name__}: {uplink}"
        return self.__class__.__name__


class SMQ(ABC):
    """Sync Message Queue base (one object per queue)."""
    _master: 'SMQC'
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

    def __init__(self, master: 'SMQC', _id: int):
        self._master = master
        self._id = _id


class SMQC:
    """Sync Message Queue Container.
     Provides SMQs uniqueness.
     """
    _child_cls: Type[SMQ]
    _store: Dict[int, SMQ] = {}
    _count: int

    def __init__(self):
        self._store = {}
        self._count = 0

    def init(self, count: int):
        self._count = count

    def q(self, i: int) -> SMQ:
        if i >= self._count:
            raise MQE(f"Too big num {i}")
        if i not in self._store:
            self._store[i] = self._child_cls(self, i)
        return self._store[i]
