"""Base for MQ engines."""
from typing import Dict, Type
from abc import ABC, abstractmethod


class QE(RuntimeError):
    """Queue Exception."""

    def __str__(self):
        """Make string representation of exception."""
        if uplink := super().__str__():
            return f"{self.__class__.__name__}: {uplink}"
        return self.__class__.__name__


class SQ(ABC):
    """Sync Queue base (one object per queue)."""
    _master: 'SQC'
    _id: int

    @abstractmethod
    def count(self) -> int:
        """Get messages count."""
        raise NotImplementedError()

    @abstractmethod
    def put(self, data: bytes):
        """Put message."""
        raise NotImplementedError()

    @abstractmethod
    def get(self, wait: bool = True) -> bytes:
        """Get a message."""
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    def __init__(self, master: 'SQC', _id: int):
        self._master = master
        self._id = _id


class SQC:
    """Sync Queue Container.
     Provides SMQs uniqueness.
     """
    _child_cls: Type[SQ]
    _store: Dict[int, SQ] = {}
    _count: int

    def __init__(self):
        self._store = {}
        self._count = 0

    def open(self, count: int):
        self._count = count

    def close(self):
        for child in self._store.values():
            child.close()
        self._store.clear()

    def q(self, i: int) -> SQ:
        if i >= self._count:
            raise QE(f"Too big num {i}")
        if i not in self._store:
            self._store[i] = self._child_cls(self, i)
        return self._store[i]