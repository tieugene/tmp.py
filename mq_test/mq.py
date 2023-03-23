"""In-Memory MQ."""
import asyncio
# 1. std
import queue
from typing import Optional

# 3. local
from bq import SQ, SQC, AQ, AQC

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

    def count(self) -> int:
        """Get messages count."""
        return self.__q.qsize()

    def put(self, data: bytes):
        """Put a message."""
        return self.__q.put(data)

    def get(self, wait: bool = True) -> Optional[bytes]:
        """Get a message."""
        try:
            return self.__q.get(block=wait, timeout=None)
        except queue.Empty as e:
            return None

    def close(self):
        ...


class MSQC(SQC):
    """Sync Memory Queue Container."""
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

    def count(self) -> int:
        """Get messages count."""
        return self.__q.qsize()

    async def put(self, data: bytes):
        """Put a message."""
        await self.__q.put(data)

    async def get(self, wait: bool = True) -> Optional[bytes]:
        """Get a message."""
        if wait:
            return await self.__q.get()
        else:
            try:
                return self.__q.get_nowait()
            except asyncio.QueueEmpty as e:
                return None

    async def get_all(self):
        ret = True
        while ret:
            ret = await self.get(False)

    async def close(self):
        ...


class MAQC(AQC):
    """Sync Memory Queue Container."""
    _child_cls = _MAQ
