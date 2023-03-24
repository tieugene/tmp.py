"""In-Memory MQ."""
import asyncio
# 1. std
import queue
from typing import Optional, Iterator
# 3. local
# from . import bq  # not works
from bq import AQC, AQ, SQ, SQC

# x. const
GET_TIMEOUT = 1  # sec


# == Sync ==
class _MSQ(SQ):
    """Memory Sync Queue.
    [RTFM](https://docs.python.org/3/library/queue.html)
    """
    __q: queue.SimpleQueue

    def __init__(self, master: 'MSQC', __id: int):
        super().__init__(master, __id)
        self.__q = queue.SimpleQueue()

    def open(self):
        ...

    def count(self) -> int:
        return self.__q.qsize()

    def put(self, data: bytes):
        self.__q.put(data)

    def get(self, wait: bool = True) -> Optional[bytes]:
        try:
            return self.__q.get(block=wait, timeout=None)
        except queue.Empty:
            return None

    def get_all(self):
        try:
            while self.__q.get(block=False):
                ...
        except queue.Empty:
            return

    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> bytes:
        if self.__q.empty():  # not guaranied
            raise StopIteration
        return self.__q.get()

    def close(self):
        ...


class MSQC(SQC):
    """Memory Sync Queue Container."""
    _child_cls = _MSQ


# == Async ==
class _MAQ(AQ):
    """Memory Async Queue.
    [RTFM](https://docs.python.org/3/library/asyncio-queue.html)
    """
    __q: asyncio.Queue

    def __init__(self, master: 'MAQC', __id: int):
        super().__init__(master, __id)
        self.__q = asyncio.Queue()

    async def open(self):
        ...

    async def count(self) -> int:
        return self.__q.qsize()

    async def put(self, data: bytes):
        await self.__q.put(data)

    async def get(self, wait: bool = True) -> Optional[bytes]:
        if wait:
            return await self.__q.get()
        else:
            try:
                return self.__q.get_nowait()
            except asyncio.QueueEmpty:
                return None

    async def get_all(self):
        ret = True
        while ret:
            ret = await self.get(False)

    async def close(self):
        ...


class MAQC(AQC):
    """Memory Async Queue Container."""
    _child_cls = _MAQ
