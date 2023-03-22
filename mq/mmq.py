"""In-Memory MQ."""
# 1. std
import queue
# 3. local
from mq.base import SMQ, SMQC
# x. const
GET_TIMEOUT = 1  # sec


class MSMQ(SMQ):
    """Memory Sync Message Queue.
    [RTFM](https://docs.python.org/3/library/queue.html)
    """
    __q: queue.SimpleQueue

    def __init__(self, master: 'MSMQC', __id: int):
        SMQ.__init__(self, master, __id)
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


class MSMQC(SMQC):
    """Sync Memory Message Queue Container."""
    _child_cls = MSMQ
