"""Base for MQ engines."""
import asyncio
from typing import Dict, Type, Optional
from abc import ABC, abstractmethod


class QE(RuntimeError):
    """Queue Exception."""

    def __str__(self):
        """Make string representation of exception."""
        if uplink := super().__str__():
            return f"{self.__class__.__name__}: {uplink}"
        return self.__class__.__name__


# == common ==
class Q:
    _master: 'QC'
    _id: int

    def __init__(self, master: 'QC', _id: int):
        self._master = master
        self._id = _id


class QC:
    """Queue Container.
     Provides Qs uniqueness.
     """
    _child_cls: Type[Q]
    _store: Dict[int, Q]
    _count: int

    def __init__(self):
        self._store = {}
        self._count = 0


# == Sync ==
class SQ(Q, ABC):
    """Sync Queue base (one object per queue)."""

    @abstractmethod
    def open(self):
        """Open."""
        raise NotImplementedError()

    @abstractmethod
    def count(self) -> int:
        """Get messages count."""
        raise NotImplementedError()

    @abstractmethod
    def put(self, data: bytes):
        """Put message."""
        raise NotImplementedError()

    @abstractmethod
    def get(self, wait: bool = True) -> Optional[bytes]:
        """Get a message."""
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    def __init__(self, master: 'SQC', _id: int):
        super().__init__(master, _id)


class SQC(QC):
    """Sync Queue Container."""
    _child_cls: Type[SQ]
    _store: Dict[int, SQ]

    def __init__(self):
        super().__init__()

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
            self._store[i].open()
        return self._store[i]


# == Async ==
class AQ(Q, ABC):
    """Async Queue base (one object per queue)."""
    _master: 'AQC'
    _id: int

    @abstractmethod
    async def open(self):
        raise NotImplementedError()

    @abstractmethod
    def count(self) -> int:  # FIXME: async
        """Get messages count."""
        raise NotImplementedError()

    @abstractmethod
    async def put(self, data: bytes):
        """Put message."""
        raise NotImplementedError()

    @abstractmethod
    async def get(self, wait: bool = True) -> Optional[bytes]:
        """Get a message."""
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self):
        """Get all message."""
        raise NotImplementedError()

    @abstractmethod
    async def close(self):
        raise NotImplementedError()

    def __init__(self, master: 'AQC', _id: int):
        super().__init__(master, _id)


class AQC(QC):
    """Async Queue Container."""
    _child_cls: Type[AQ]
    _store: Dict[int, AQ]

    def __init__(self):
        super().__init__()

    async def open(self, count: int):
        self._count = count

    async def close(self):
        await asyncio.gather(*[child.close() for child in self._store.values()])
        self._store.clear()

    async def q(self, i: int) -> AQ:
        if i >= self._count:
            raise QE(f"Too big num {i}")
        if i not in self._store:
            self._store[i] = self._child_cls(self, i)
            await self._store[i].open()
        return self._store[i]
