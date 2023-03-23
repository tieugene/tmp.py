"""Disk-based implementation."""
# 2. 3rd
import queuelib
import persistqueue
# 3. local
from . import bq


# == queuelib ==
class _D1SQ(bq.SQ):
    """Disk-based #1 Sync Queue.
    1. [queuelib](https://github.com/scrapy/queuelib)
    """
    __q: queuelib.FifoDiskQueue

    def __init__(self, master: 'D1SQC', __id: int):
        super().__init__(master, __id)
        self.__q = queuelib.FifoDiskQueue(f"_d1sd/{__id:04d}")

    def count(self) -> int:
        """Get messages count."""
        return len(self.__q)

    def put(self, data: bytes):
        """Put a message."""
        return self.__q.push(data)

    def get(self, wait: bool = True) -> bytes:
        """Get a message."""
        return self.__q.pop()

    def close(self):
        self.__q.close()


class D1SQC(bq.SQC):
    """Disk-based #1 Queue Container."""
    _child_cls = _D1SQ


# == persistqueue ==
class _D2SQ(bq.SQ):
    """Disk-based #2 Sync Queue.
    2. [persistqueue](https://github.com/peter-wangxu/persist-queue)
    """
    __q: persistqueue.Queue

    def __init__(self, master: 'D2SQC', __id: int):
        super().__init__(master, __id)
        self.__q = persistqueue.Queue(f"_d2sd/{__id:04d}", autosave=True)  # FIXME: use .task_done()

    def count(self) -> int:
        """Get messages count."""
        return self.__q.qsize()

    def put(self, data: bytes):
        """Put a message."""
        return self.__q.put(data)

    def get(self, wait: bool = True) -> bytes:
        """Get a message."""
        return self.__q.get(wait)

    def close(self):
        ...


class D2SQC(bq.SQC):
    """Disk-based #2 Sync Queue Container."""
    _child_cls = _D2SQ
