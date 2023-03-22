"""In-Memory MQ."""
# 1. std
import queue
# 3. local
from bq import SQ, SQC
# x. const
GET_TIMEOUT = 1  # sec


class _MSQ(SQ):
    """Memory Sync Queue.
    [RTFM](https://docs.python.org/3/library/queue.html)
    """
    __q: queue.SimpleQueue

    def __init__(self, master: 'MSQC', __id: int):
        SQ.__init__(self, master, __id)
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

    def close(self):
        ...


class MSQC(SQC):
    """Sync Memory Queue Container."""
    _child_cls = _MSQ
