"""In-Memory MQ.
- collections.deque
- [queue.SimpleQueue](https://docs.python.org/3/library/queue.html)
- [asyncio.Queue](https://docs.python.org/3/library/asyncio-queue.html#examples)
"""
# 1. std
from typing import Dict
import queue
# 3. local
from mq.base import MQE, MQ, MQCollection

# x. const
GET_TIMEOUT = 1  # sec


class MMQ(MQ):
    """Queue itself (one object per queue)."""
    __q: queue.SimpleQueue

    def __init__(self, master: 'MMQCollection', __id: int):
        MQ.__init__(self, master, __id)
        self.__q = queue.SimpleQueue()

    def count(self) -> int:
        """Get messages count."""
        return self.__q.qsize()

    def put(self, data: bytes):
        """Put a message."""
        return self.__q.put(data)

    def get(self, wait: bool = True) -> bytes:
        """Get a message."""
        return self.__q.get(block=wait, timeout=None)


class MMQCollection(MQCollection):
    """Container to uniq MQs."""

    def __init__(self):
        super().__init__(MMQ)
